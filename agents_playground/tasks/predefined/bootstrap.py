from array import array as create_array
from fractions import Fraction
import logging
from math import radians
import os
from pathlib import Path
from typing import cast

import wgpu
from wgpu import (
    gpu,
    GPUBuffer,
    GPUCanvasContext,
    GPUCommandEncoder,
    GPUDevice,
    GPUPipelineLayout,
    GPUQueue,
    GPURenderPassEncoder,
    GPURenderPipeline,
    GPUTexture,
)
from wgpu import GPUDevice
from wgpu.gui.wx import WgpuWidget

from agents_playground.core.webgpu_sim_loop import WGPUSimLoop
from agents_playground.fp import Something
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.camera_configuration.camera_configuration_builder import (
    CameraConfigurationBuilder,
)
from agents_playground.gpu.mesh_configuration.builders.triangle_list_mesh_configuration_builder import (
    TriangleListMeshConfigurationBuilder,
)
from agents_playground.gpu.renderer_builders.renderer_builder import (
    assemble_camera_data,
)
from agents_playground.gpu.renderers.landscape_renderer import LandscapeRenderer
from agents_playground.gpu.shader_configuration.default_shader_configuration_builder import (
    DefaultShaderConfigurationBuilder,
)
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.shaders import load_shader
from agents_playground.loaders.scene_loader import SceneLoader
from agents_playground.scene import Scene
from agents_playground.simulation.context import SimulationContext, UniformRegistry
from agents_playground.simulation.sim_state import SimulationState
from agents_playground.spatial.landscape import cubic_tile_to_vertices
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.mesh import MeshBuffer, MeshData, MeshLike, MeshRegistry
from agents_playground.spatial.mesh.half_edge_mesh import (
    HalfEdgeMesh,
    MeshWindingDirection,
)
from agents_playground.spatial.mesh.packers.normal_packer import NormalPacker
from agents_playground.spatial.mesh.packers.simple_mesh_packer import SimpleMeshPacker
from agents_playground.spatial.mesh.tesselator import FanTesselator
from agents_playground.sys.logger import get_default_logger, log_call
from agents_playground.tasks.graph import TaskGraph
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import TaskResource

logger: logging.Logger = get_default_logger()


@task_input(type=str, name="scene_file_path")
@task_output(type=Scene, name="scene")
@task()
def load_scene(task_graph: TaskGraph) -> None:
    """
    A task that is responsible for parsing the provided scene file.

    Effects:
    - The JSON scene file that is provided as an input is parsed.
    - The resulting Scene instance is allocated as an output.
    """
    # Get the inputs
    scene_file_path_resource: TaskResource = task_graph.resource_tracker[
        "scene_file_path"
    ]
    scene_path = scene_file_path_resource.resource.unwrap()

    # Load the Scene.
    scene_loader = SceneLoader()
    scene: Scene = scene_loader.load(scene_path)

    # Allocate the task outputs.
    task_graph.provision_resource("scene", instance=scene)


@task_input(type=Scene, name="scene")
@task_output(type=MeshData, name="landscape")
@task_output(type=MeshData, name="landscape_tri_mesh")
@task(require_before=["load_scene"])
def load_landscape_mesh(task_graph: TaskGraph) -> None:
    """Build a half-edge mesh of the landscape."""
    scene: Scene = task_graph.resource_tracker["scene"].resource.unwrap()

    landscape_resource: TaskResource = task_graph.provision_resource("landscape")
    landscape: MeshData = cast(MeshData, landscape_resource.resource.unwrap())

    landscape_lattice_mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CW)
    for tile in scene.landscape.tiles.values():
        tile_vertices = cubic_tile_to_vertices(tile, scene.landscape.characteristics)
        landscape_lattice_mesh.add_polygon(tile_vertices)
    landscape.mesh = Something(landscape_lattice_mesh)

    # 2. Tesselate the landscape.
    landscape_tri_mesh: MeshLike = landscape_lattice_mesh.deep_copy()
    FanTesselator().tesselate(landscape_tri_mesh)

    # 4. Calculate the normals for the tessellated landscape mesh.
    landscape_tri_mesh.calculate_face_normals()
    landscape_tri_mesh.calculate_vertex_normals()

    landscape_tri_mesh_resource: TaskResource = task_graph.provision_resource(
        "landscape_tri_mesh"
    )
    landscape_tri_mesh_data: MeshData = cast(
        MeshData, landscape_tri_mesh_resource.resource.unwrap()
    )
    landscape_tri_mesh_data.lod = 1
    landscape_tri_mesh_data.mesh_previous_lod_alias = Something("landscape")
    landscape_tri_mesh_data.mesh = Something(landscape_tri_mesh)
    landscape_tri_mesh_data.vertex_buffer = Something(
        SimpleMeshPacker().pack(landscape_tri_mesh)
    )
    landscape_tri_mesh_data.normals_buffer = Something(
        NormalPacker().pack(landscape_tri_mesh)
    )

    landscape.next_lod_alias = Something("landscape_tri_mesh")


@task_input(type=WgpuWidget, name="canvas")
@task_output(type=GPUDevice, name="gpu_device")
@task_output(type=str, name="render_texture_format")
@task(require_before=["load_landscape_mesh"])
def initialize_graphics_pipeline(task_graph: TaskGraph) -> None:
    """
    A task responsible for initializing the graphics pipeline.
    """
    # Initialize the graphics pipeline via WebGPU.
    canvas: WgpuWidget = task_graph.resource_tracker["canvas"].resource.unwrap()

    # Create a high performance GPUAdapter for a Canvas.
    adapter: GPUAdapter = gpu.request_adapter(  # type: ignore
        canvas=canvas, power_preference="high-performance"
    )

    # Get an instance of the GPUDevice that is associated with a provided GPUAdapter.
    device: GPUDevice = adapter.request_device(
        label="only-gpu-device",
        required_features=[],
        required_limits={},
        default_queue={},
    )

    canvas_context: GPUCanvasContext = canvas.get_context()

    # Set the GPUCanvasConfiguration to control how drawing is done.
    render_texture_format: str = canvas_context.get_preferred_format(device.adapter)

    canvas_context.configure(
        device=device,
        usage=wgpu.flags.TextureUsage.RENDER_ATTACHMENT,  # type: ignore
        format=render_texture_format,
        view_formats=[],
        color_space="bgra8unorm-srgb",
        alpha_mode="opaque",
    )

    task_graph.provision_resource("gpu_device", instance=device)
    task_graph.provision_resource(
        "render_texture_format", instance=render_texture_format
    )


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
def prepare_landscape_renderer(task_graph: TaskGraph) -> None:
    """
    A task that is responsible for building the renderer specific to the landscape.
    """
    # Get the inputs
    scene: Scene = task_graph.resource_tracker["scene"].resource.unwrap()
    device: GPUDevice = task_graph.resource_tracker["gpu_device"].resource.unwrap()
    render_texture_format: str = task_graph.resource_tracker[
        "render_texture_format"
    ].resource.unwrap()

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
    landscape_tri_mesh: MeshData = task_graph.resource_tracker[
        "landscape_tri_mesh"
    ].resource.unwrap()

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
    task_graph.provision_resource(name="camera_uniforms", instance=camera_buffer)
    task_graph.provision_resource(
        name="display_configuration_buffer", instance=display_config_buffer
    )
    task_graph.provision_resource(
        "landscape_rendering_pipeline", instance=rendering_pipeline
    )
    task_graph.provision_resource("landscape_renderer", instance=landscape_renderer)


# fmt: off
@task_input( type=Scene,             name="scene")
@task_input( type=WgpuWidget,        name="canvas")
@task_input( type=str,               name="render_texture_format")
@task_input( type=GPUDevice,         name="gpu_device")
@task_output(type=SimulationContext, name="simulation_context")
@task()
# fmt: on
# TODO: Re-evaluate if the engine still needs a simulation context.
# It might make sense to have a FrameContext.
def create_simulation_context(task_graph: TaskGraph) -> None:
    # Get the inputs
    scene: Scene = task_graph.resource_tracker["scene"].resource.unwrap()
    canvas: WgpuWidget = task_graph.resource_tracker["canvas"].resource.unwrap()
    render_texture_format: str = task_graph.resource_tracker[
        "render_texture_format"
    ].resource.unwrap()
    device: GPUDevice = task_graph.resource_tracker["gpu_device"].resource.unwrap()

    sc = SimulationContext(
        scene=scene,
        canvas=canvas,
        render_texture_format=render_texture_format,
        device=device,
        mesh_registry=MeshRegistry(),
        extensions={},
        uniforms=UniformRegistry(),
    )

    # Register the output
    task_graph.provision_resource(name="simulation_context", instance=sc)


class TaskDrivenRenderer:
    @log_call
    def __init__(self, context: SimulationContext, task_graph: TaskGraph) -> None:
        self._context = context
        self._task_graph = task_graph
        self._render_tasks = [
            "calculate_aspect_ratio",
            "set_texture_target",
            "construct_projection_matrix",
            "bind_camera_data",
            "configure_color_attachment",
            "create_depth_texture",
            "create_depth_stencil_attachment",
            "create_gpu_encoder",
            "create_render_pass_encoder",
            "render_landscape",
            "end_render_pass",
        ]

    @log_call
    def render(self) -> None:
        """
        I think what I want here is to repeat the task graph pattern
        but with just render tasks.

        I suspect that I'll be able to ditch the SimulationContext instance.
        """
        for task_name in self._render_tasks:
            self._task_graph.provision_task(task_name)
        self._task_graph.run_until_done()


@task_input(type=WgpuWidget, name="canvas")
@task_input(type=SimulationContext, name="simulation_context")
@task_output(type=WGPUSimLoop, name="sim_loop")
@task_output(type=TaskDrivenRenderer, name="task_renderer")
@task(pin_to_main_thread=True)
def start_simulation_loop(task_graph: TaskGraph) -> None:
    sim_context: SimulationContext = task_graph.resource_tracker[
        "simulation_context"
    ].resource.unwrap()

    canvas: WgpuWidget = task_graph.resource_tracker["canvas"].resource.unwrap()

    # Create the top level renderer and bind it to the canvas.
    task_renderer = TaskDrivenRenderer(sim_context, task_graph)
    canvas.request_draw(task_renderer.render)

    sim_loop = WGPUSimLoop(window=canvas)

    # Register the outputs
    task_graph.provision_resource(name="task_renderer", instance=task_renderer)
    task_graph.provision_resource(name="sim_loop", instance=sim_loop)

    # Start the simulation loop. Note that this spins up a new thread.
    sim_loop.simulation_state = SimulationState.RUNNING
    sim_loop.start(sim_context)


@task_output(type=WGPUSimLoop, name="sim_loop")
@task(pin_to_main_thread=True)
def end_simulation(task_graph: TaskGraph) -> None:
    sim_loop: WGPUSimLoop = task_graph.resource_tracker["sim_loop"].resource.unwrap()
    sim_loop.end()


@task(pin_to_main_thread=True, require_before=["end_simulation"])
def clear_task_graph(task_graph: TaskGraph) -> None:
    """
    Deletes all provisioned resources and tasks and removes all registrations.
    Basically, resets the task graph to be empty.
    """
    task_graph.clear()


@task_input(type=WgpuWidget, name="canvas")
@task_output(type=Fraction, name="aspect_ratio")
@task()
def calculate_aspect_ratio(task_graph: TaskGraph) -> None:
    """Calculate the current aspect ratio."""
    canvas: WgpuWidget = task_graph.resource_tracker["canvas"].resource.unwrap()
    canvas_width, canvas_height = canvas.GetSize()
    aspect_ratio = Fraction(canvas_width, canvas_height)
    task_graph.provision_resource("aspect_ratio", instance=aspect_ratio)


@task_input(type=WgpuWidget, name="canvas")
@task_output(type=GPUTexture, name="texture_target")
@task()
def set_texture_target(task_graph: TaskGraph) -> None:
    canvas: WgpuWidget = task_graph.resource_tracker["canvas"].resource.unwrap()
    canvas_context: GPUCanvasContext = canvas.get_context()
    current_texture: GPUTexture = canvas_context.get_current_texture()
    task_graph.provision_resource("texture_target", instance=current_texture)


@task_input(type=Scene, name="scene")
@task_input(type=Fraction, name="aspect_ratio")
@task()
def construct_projection_matrix(task_graph: TaskGraph) -> None:
    scene: Scene = task_graph.resource_tracker["scene"].resource.unwrap()

    aspect_ratio: Fraction = task_graph.resource_tracker[
        "aspect_ratio"
    ].resource.unwrap()

    scene.camera.projection_matrix = Something(
        Matrix4x4.perspective(
            aspect_ratio=aspect_ratio, v_fov=radians(72.0), near=0.1, far=100.0
        )
    )


@task_input(type=Scene, name="scene")
@task_input(type=GPUDevice, name="gpu_device")
@task_input(type=Fraction, name="aspect_ratio")
@task_input(type=GPUBuffer, name="camera_uniforms")
@task()
def bind_camera_data(task_graph: TaskGraph) -> None:
    scene: Scene = task_graph.resource_tracker["scene"].resource.unwrap()
    device: GPUDevice = task_graph.resource_tracker["gpu_device"].resource.unwrap()
    camera_uniforms: GPUBuffer = task_graph.resource_tracker[
        "camera_uniforms"
    ].resource.unwrap()

    camera_data = assemble_camera_data(scene.camera)
    device.queue.write_buffer(camera_uniforms, 0, camera_data)


@task_input(type=GPUTexture, name="texture_target")
@task_output(type=dict, name="color_attachment")
@task()
def configure_color_attachment(task_graph: TaskGraph) -> None:
    """Build a render pass color attachment."""
    current_texture: GPUTexture = task_graph.resource_tracker[
        "texture_target"
    ].resource.unwrap()

    # struct.RenderPassColorAttachment
    color_attachment = {
        "view": current_texture.create_view(),
        "resolve_target": None,
        "clear_value": (0.9, 0.5, 0.5, 1.0),  # Clear to pink.
        "load_op": wgpu.LoadOp.clear,  # type: ignore
        "store_op": wgpu.StoreOp.store,  # type: ignore
    }

    task_graph.provision_resource("color_attachment", instance=color_attachment)


@task_input(type=GPUDevice, name="gpu_device")
@task_input(type=GPUTexture, name="texture_target")
@task_output(type=GPUTexture, name="depth_texture")
@task()
def create_depth_texture(task_graph: TaskGraph) -> None:
    """Create a depth texture for the Z-Buffer."""
    device: GPUDevice = task_graph.resource_tracker["gpu_device"].resource.unwrap()
    current_texture: GPUTexture = task_graph.resource_tracker[
        "texture_target"
    ].resource.unwrap()

    depth_texture: wgpu.GPUTexture = device.create_texture(
        label="Z Buffer Texture",
        size=current_texture.size,
        usage=wgpu.TextureUsage.RENDER_ATTACHMENT,  # type: ignore
        format=wgpu.enums.TextureFormat.depth24plus_stencil8,  # type: ignore
    )

    task_graph.provision_resource("depth_texture", instance=depth_texture)


@task_input(type=GPUTexture, name="depth_texture")
@task_output(type=dict, name="depth_stencil_attachment")
@task()
def create_depth_stencil_attachment(task_graph: TaskGraph) -> None:
    """Create a depth stencil attachment."""
    depth_texture: GPUTexture = task_graph.resource_tracker[
        "depth_texture"
    ].resource.unwrap()

    depth_texture_view = depth_texture.create_view()
    depth_stencil_attachment = {
        "view": depth_texture_view,
        "depth_clear_value": 1.0,
        "depth_load_op": wgpu.LoadOp.clear,  # type: ignore
        "depth_store_op": wgpu.StoreOp.store,  # type: ignore
        "depth_read_only": False,
        # I'm not sure about these values.
        "stencil_clear_value": 0,
        "stencil_load_op": wgpu.LoadOp.load,  # type: ignore
        "stencil_store_op": wgpu.StoreOp.store,  # type: ignore
        "stencil_read_only": False,
    }

    task_graph.provision_resource(
        "depth_stencil_attachment", instance=depth_stencil_attachment
    )


@task_input(type=GPUDevice, name="gpu_device")
@task_output(type=GPUCommandEncoder, name="command_encoder")
@task()
def create_gpu_encoder(task_graph: TaskGraph) -> None:
    """Create a GPU command encoder."""
    device: GPUDevice = task_graph.resource_tracker["gpu_device"].resource.unwrap()
    command_encoder: wgpu.GPUCommandEncoder = device.create_command_encoder()
    task_graph.provision_resource("command_encoder", instance=command_encoder)


@task_input(type=GPUCommandEncoder, name="command_encoder")
@task_input(type=dict, name="color_attachment")
@task_input(type=dict, name="depth_stencil_attachment")
@task_output(type=GPURenderPassEncoder, name="render_pass_encoder")
@task()
def create_render_pass_encoder(task_graph: TaskGraph) -> None:
    """Encode the drawing instructions."""
    command_encoder: GPUCommandEncoder = task_graph.resource_tracker[
        "command_encoder"
    ].resource.unwrap()
    color_attachment: dict = task_graph.resource_tracker[
        "color_attachment"
    ].resource.unwrap()
    depth_stencil_attachment: dict = task_graph.resource_tracker[
        "depth_stencil_attachment"
    ].resource.unwrap()

    # The first command to encode is the instruction to do a rendering pass.
    render_pass_encoder: GPURenderPassEncoder = command_encoder.begin_render_pass(
        label="Draw Frame Render Pass",
        color_attachments=[color_attachment],
        depth_stencil_attachment=depth_stencil_attachment,
        occlusion_query_set=None,  # type: ignore
        timestamp_writes=None,
        max_draw_count=50_000_000,  # Default
    )

    task_graph.provision_resource("render_pass_encoder", instance=render_pass_encoder)


@task_input(type=MeshData, name="landscape_tri_mesh")
@task_input(type=GPURenderer, name="landscape_renderer")
@task_input(type=GPURenderPassEncoder, name="render_pass_encoder")
@task()
def render_landscape(task_graph: TaskGraph) -> None:
    """Render the landscape to the active render pass."""
    # Set the landscape rendering pipe line as the active one.
    # Encode the landscape drawing instructions.
    landscape_renderer: GPURenderer = task_graph.resource_tracker[
        "landscape_renderer"
    ].resource.unwrap()

    render_pass_encoder: GPURenderPassEncoder = task_graph.resource_tracker[
        "render_pass_encoder"
    ].resource.unwrap()

    landscape_tri_mesh: MeshData = task_graph.resource_tracker[
        "landscape_tri_mesh"
    ].resource.unwrap()

    render_pass_encoder.set_pipeline(landscape_renderer.render_pipeline)
    landscape_renderer.render(render_pass_encoder, landscape_tri_mesh)


@task_input(type=GPUDevice, name="gpu_device")
@task_input(type=GPUCommandEncoder, name="command_encoder")
@task_input(type=GPURenderPassEncoder, name="render_pass_encoder")
@task(require_before=["render_landscape"])
def end_render_pass(task_graph: TaskGraph) -> None:
    """Submit the draw calls to the GPU."""
    device: GPUDevice = task_graph.resource_tracker["gpu_device"].resource.unwrap()
    render_pass_encoder: GPURenderPassEncoder = task_graph.resource_tracker[
        "render_pass_encoder"
    ].resource.unwrap()

    command_encoder: GPUCommandEncoder = task_graph.resource_tracker[
        "command_encoder"
    ].resource.unwrap()
    render_pass_encoder.end()
    device.queue.submit([command_encoder.finish()])
