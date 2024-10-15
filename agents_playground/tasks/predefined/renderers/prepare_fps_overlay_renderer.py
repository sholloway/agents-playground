import os
from pathlib import Path
import wgpu
from wgpu import (
    GPUBuffer,
    GPUDevice,
    GPUPipelineLayout,
    GPUQueue,
    GPURenderPassEncoder,
    GPURenderPipeline,
)

from agents_playground.fp import Something
from agents_playground.gpu.mesh_configuration.builders.triangle_list_mesh_configuration_builder import (
    TriangleListMeshConfigurationBuilder,
)
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.renderers.text_renderer import (
    TextRenderer,
    TextRendererBindGroups,
    TextRendererPipelineConfiguration,
)
from agents_playground.gpu.shaders import load_shader
from agents_playground.spatial.mesh import MeshBuffer, MeshData
from agents_playground.spatial.mesh.buffers.text_buffer import TextBuffer
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import TaskGraphLike, TaskInputs, TaskOutputs


# fmt: off
@task_input( type=str,               name="render_texture_format")
@task_input( type=GPUDevice,         name="gpu_device")
@task_input( type=GPUBuffer,         name="camera_uniforms")
@task_output(type=MeshData,          name="fps_text_data")
@task_output(type=GPURenderer,       name="fps_text_renderer")
@task_output(type=GPURenderPipeline, name="fps_text_renderer_rendering_pipeline")
@task_output(type=GPUBuffer,         name="fps_text_viewport_buffer")
@task_output(type=GPUBuffer,         name="fps_text_overlay_config_buffer")
@task()
def prepare_fps_overlay_renderer(
    task_graph: TaskGraphLike, 
    inputs: TaskInputs, 
    outputs: TaskOutputs
) -> None:
# fmt: on
    # Get the inputs
    render_texture_format: str = inputs.render_texture_format
    device: GPUDevice = inputs.gpu_device
    camera_uniforms: GPUBuffer = inputs.camera_uniforms

    # Create the configuration objects
    pc = TextRendererPipelineConfiguration()
    mesh_config = TriangleListMeshConfigurationBuilder("FPS Text Renderer")

    # Load Shaders
    shader_path = os.path.join(
        Path.cwd(), "agents_playground/gpu/shaders/generic_text.wgsl"
    )
    pc.shader = load_shader(shader_path, "Generic Text Shader", device)

    # Build the Pipeline Configuration
    pc.vertex_config = {
        "module": pc.shader,
        "entry_point": "vs_main",
        "constants": {},
        "buffers": []
    }
    pc.fragment_config = {
        "module": pc.shader,
        "entry_point": "fs_main",
        "targets": [
            {
                "format": render_texture_format,
                "blend": {
                    "color":{
                        "src_factor": wgpu.BlendFactor.src_alpha, # type: ignore
                        "dst_factor": wgpu.BlendFactor.one_minus_src_alpha, # type: ignore
                        "operation": wgpu.BlendOperation.add # type: ignore
                    },
                    "alpha": {
                        "src_factor": wgpu.BlendFactor.one, # type: ignore
                        "dst_factor": wgpu.BlendFactor.one_minus_src_alpha, # type: ignore
                        "operation": wgpu.BlendOperation.add # type: ignore
                    }
                }
            }
        ],
    }

    # Load the 3D mesh into a GPUVertexBuffer.
    vertex_buffer: MeshBuffer = TextBuffer()
    fps_text_data: MeshData = MeshData() 
    fps_text_data.vertex_buffer = Something(vertex_buffer)

    # Setup Viewport Buffer
    viewport_buffer = device.create_buffer(
        label="FPS Text Renderer Viewport Buffer",
        size=8, # Width (f32) + Height (f32)
        usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,  # type: ignore
    )

    pc.bind_group_layouts['viewport_bind_group_layout'] = device.create_bind_group_layout(
        label = "Overlay Viewport Bind Group Layout",
        entries = [
            {
                "binding": 0,
                "visibility": wgpu.flags.ShaderStage.VERTEX | wgpu.flags.ShaderStage.FRAGMENT,  # type: ignore
                "buffer": {"type": wgpu.BufferBindingType.uniform},  # type: ignore
            }
        ]
    )

    # Setup Configuration Buffer
    # Note that the configuration buffer is used to specify:
    # - loc_x (f32) + loc_y (f32)
    # - Width (f32) + Height (f32) 
    # - background_color (vec4<f32>) + foreground_color(vec4<f32>)
    loc_x_size = loc_y_size = overlay_width_size = overlay_height_size =  4 # Each component is an f32.
    background_color = foreground_color = 4 * 4 # each component is a vec4<f32>
    config_buffer_components = (loc_x_size, loc_y_size, overlay_width_size, overlay_height_size, background_color, foreground_color )
    config_buffer_size: int = sum(config_buffer_components)

    fps_text_overlay_config_buffer = device.create_buffer(
        label="FPS Text Renderer Configuration Buffer",
        size=config_buffer_size,
        usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,  # type: ignore
    )

    pc.bind_group_layouts['overlay_config_bind_group_layout'] = device.create_bind_group_layout(
        label = "FPS Text Renderer Configuration Bind Group Layout",
        entries = [
            {
                "binding": 0,
                "visibility": wgpu.flags.ShaderStage.VERTEX | wgpu.flags.ShaderStage.FRAGMENT,  # type: ignore
                "buffer": {"type": wgpu.BufferBindingType.uniform},  # type: ignore
            }
        ]
    )

    # Setup the rendering pipeline
    pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(
        label="FPS Text Renderer Render Pipeline Layout",
        bind_group_layouts=[
            pc.bind_group_layouts['viewport_bind_group_layout'], 
            pc.bind_group_layouts['overlay_config_bind_group_layout']
        ]
    )

    depth_stencil_config = {
        "format": wgpu.enums.TextureFormat.depth24plus_stencil8,  # type: ignore
        "depth_write_enabled": True,
        "depth_compare": wgpu.enums.CompareFunction.less,  # type: ignore
    }

    rendering_pipeline: GPURenderPipeline = device.create_render_pipeline(
        label="FPS Text Renderer Rendering Pipeline",
        layout=pipeline_layout,
        vertex=pc.vertex_config,
        fragment=pc.fragment_config,
        depth_stencil=depth_stencil_config,
        multisample=None
    ) 

    # Create Viewport Bind Group
    vertex_buffer.bind_groups[TextRendererBindGroups.VIEWPORT] = device.create_bind_group(
        label="FPS Text Renderer Viewport Bind Group",
        layout=pc.bind_group_layouts['viewport_bind_group_layout'],
        entries=[
            {
                "binding": 0,
                "resource": {
                    "buffer": viewport_buffer,
                    "offset": 0,
                    "size":   viewport_buffer.size,
                },
            }
        ],
    )

    # Create Configuration Bind Group
    vertex_buffer.bind_groups[TextRendererBindGroups.CONFIG] = device.create_bind_group(
            label="FPS Text Renderer Configuration Bind Group",
            layout=pc.bind_group_layouts['overlay_config_bind_group_layout'],
            entries=[
                {
                    "binding": 0,
                    "resource": {
                        "buffer": fps_text_overlay_config_buffer,
                        "offset": 0,
                        "size": fps_text_overlay_config_buffer.size,
                    },
                }
            ],
        )

    # Build the FPS Text Renderer
    text_renderer: GPURenderer = TextRenderer(rendering_pipeline)

    # Track Outputs
    outputs.fps_text_data = fps_text_data
    outputs.fps_text_viewport_buffer = viewport_buffer
    outputs.fps_text_overlay_config_buffer = fps_text_overlay_config_buffer
    outputs.fps_text_renderer_rendering_pipeline = rendering_pipeline
    outputs.fps_text_renderer = text_renderer
