from array import array as create_array
import os
from pathlib import Path
import wgpu
from wgpu import (
    GPUBuffer,
    GPUDevice,
    GPUPipelineLayout,
    GPUQueue,
    GPURenderPipeline,
)

from agents_playground.fp import Something
from agents_playground.gpu.camera_configuration.camera_configuration_builder import CameraConfigurationBuilder
from agents_playground.gpu.mesh_configuration.builders.triangle_list_mesh_configuration_builder import TriangleListMeshConfigurationBuilder
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.renderer_builder import assemble_camera_data
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.renderers.landscape_renderer import LandscapeRenderer
from agents_playground.gpu.shader_configuration.default_shader_configuration_builder import DefaultShaderConfigurationBuilder
from agents_playground.gpu.shaders import load_shader
from agents_playground.scene import Scene
from agents_playground.spatial.mesh import MeshBuffer, MeshData
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import TaskGraphLike, TaskInputs, TaskOutputs

# fmt: off
@task_input( type=Scene,             name="scene")
@task_input( type=MeshData,          name="landscape_tri_mesh")
@task_input( type=str,               name="render_texture_format")
@task_input( type=GPUDevice,         name="gpu_device")
@task_output(type=GPURenderer,       name="landscape_renderer")
@task_output(type=GPUPipelineLayout, name="landscape_rendering_pipeline")
@task_output(type=GPUBuffer,         name="camera_uniforms")
@task_output(type=GPUBuffer,         name="display_configuration_buffer")
@task(require_before=["initialize_graphics_pipeline"])
# fmt: on
def prepare_landscape_renderer(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """
    A task that is responsible for building the renderer specific to the landscape.
    """
    # Get the inputs
    scene: Scene = inputs.scene
    device: GPUDevice = inputs.gpu_device
    render_texture_format: str = inputs.render_texture_format
    landscape_tri_mesh: MeshData = inputs.landscape_tri_mesh

    # Create the configuration objects
    pc = PipelineConfiguration()
    camera_config = CameraConfigurationBuilder()
    shader_config = DefaultShaderConfigurationBuilder()
    mesh_config = TriangleListMeshConfigurationBuilder("Landscape")

    # Load Shaders
    shader_path = os.path.join(
        Path.cwd(), "agents_playground/gpu/shaders/landscape.wgsl"
    )

    pc.shader = load_shader(shader_path, "Triangle Shader", device)

    # Build the Pipeline Configuration
    pc.primitive_config = mesh_config.configure_pipeline_primitives()
    pc.vertex_config = shader_config.configure_vertex_shader(pc.shader)
    pc.fragment_config = shader_config.configure_fragment_shader(
        render_texture_format, pc.shader
    )

    # Load the 3D mesh into a GPUVertexBuffer.
    vertex_buffer: MeshBuffer = landscape_tri_mesh.vertex_buffer.unwrap()
    vertex_buffer.vbo = mesh_config.create_vertex_buffer(device, vertex_buffer.data)
    vertex_buffer.ibo = mesh_config.create_index_buffer(device, vertex_buffer.index)

    # Setup the Camera
    # TODO: All the renderers will try to do this.
    # This should be it's own task to
    pc.camera_data = assemble_camera_data(scene.camera)
    camera_buffer: GPUBuffer = camera_config.create_camera_buffer(device, scene.camera)

    # Setup the model transform
    # TODO: This should probably not be on the Scene object at this point.
    # Perhaps make this a registered resource?
    scene.landscape_transformation.transformation_buffer = Something(
        device.create_buffer(
            label="Landscape Model Transform Buffer",
            size=4 * 16,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,  # type: ignore
        )
    )

    # Set up the bind group layout for the uniforms.
    pc.camera_uniform_bind_group_layout = camera_config.create_camera_ubg_layout(device)

    pc.model_uniform_bind_group_layout = camera_config.create_model_ubg_layout(device)

    pc.display_config_bind_group_layout = device.create_bind_group_layout(
        label="Display Configuration Uniform Bind Group Layout",
        entries=[
            {
                "binding": 0,  # Bind group for the display configuration options.
                "visibility": wgpu.flags.ShaderStage.VERTEX | wgpu.flags.ShaderStage.FRAGMENT,  # type: ignore
                "buffer": {"type": wgpu.BufferBindingType.uniform},  # type: ignore
            }
        ],
    )

    display_config_buffer: GPUBuffer = device.create_buffer(
        label="Display Configuration Buffer",
        size=4,
        usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,  # type: ignore
    )

    # Create the rendering pipeline.
    pipeline_layout: GPUPipelineLayout = device.create_pipeline_layout(
        label="Landscape Render Pipeline Layout",
        bind_group_layouts=[
            pc.camera_uniform_bind_group_layout,
            pc.model_uniform_bind_group_layout,
            pc.display_config_bind_group_layout,
        ],
    )

    depth_stencil_config = {
        "format": wgpu.enums.TextureFormat.depth24plus_stencil8,  # type: ignore
        "depth_write_enabled": True,
        "depth_compare": wgpu.enums.CompareFunction.less,  # type: ignore
    }

    rendering_pipeline: GPURenderPipeline = device.create_render_pipeline(
        label="Landscape Rendering Pipeline",
        layout=pipeline_layout,
        primitive=pc.primitive_config,
        vertex=pc.vertex_config,
        fragment=pc.fragment_config,
        depth_stencil=depth_stencil_config,
        multisample=None,
    )

    # Create Bind Groups
    vertex_buffer.bind_groups[0] = camera_config.create_camera_bind_group(
        device, pc.camera_uniform_bind_group_layout, camera_buffer
    )

    vertex_buffer.bind_groups[1] = camera_config.create_model_transform_bind_group(
        device,
        pc.model_uniform_bind_group_layout,
        scene.landscape_transformation.transformation_buffer.unwrap(),  # TODO: Move this buffer off the scene and into the resource tracker.
    )

    vertex_buffer.bind_groups[2] = device.create_bind_group(
        label="Display Configuration Bind Group",
        layout=pc.display_config_bind_group_layout,
        entries=[
            {
                "binding": 0,
                "resource": {
                    "buffer": display_config_buffer,
                    "offset": 0,
                    "size": display_config_buffer.size,
                },
            }
        ],
    )

    # Load Uniform Buffers
    queue: GPUQueue = device.queue
    queue.write_buffer(camera_buffer, 0, pc.camera_data)

    # TODO: Move this buffer off the scene and into the resource tracker.
    if not scene.landscape_transformation.transformation_data.is_something():
        scene.landscape_transformation.transform()

    # TODO: Move this buffer off the scene and into the resource tracker.
    queue.write_buffer(
        scene.landscape_transformation.transformation_buffer.unwrap(),
        0,
        scene.landscape_transformation.transformation_data.unwrap(),
    )

    queue.write_buffer(display_config_buffer, 0, create_array("i", [0]))

    # Construct the LandscapeRender
    landscape_renderer: GPURenderer = LandscapeRenderer(rendering_pipeline)

    # Set the outputs.
    outputs.camera_uniforms = camera_buffer
    outputs.display_configuration_buffer = display_config_buffer
    outputs.landscape_rendering_pipeline = rendering_pipeline
    outputs.landscape_renderer = landscape_renderer
