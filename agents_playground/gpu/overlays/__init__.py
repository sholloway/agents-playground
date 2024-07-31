from dataclasses import dataclass
from enum import IntEnum, StrEnum
import os
from pathlib import Path
import wgpu
import wgpu.backends.wgpu_native

from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.shaders import load_shader
from agents_playground.scene import Scene

"""
For now, just get an overlay that is a solid color that is constrained to a fixed space.
"""
class OverlayBindGroups(IntEnum):
    VIEWPORT = 0

class OverlayBufferNames(StrEnum):
    VIEWPORT = "viewport_buffer"

class Overlay:
    def __init__(self) -> None:
        self._render_pipeline: wgpu.GPURenderPipeline
        self._builder = OverlayBuilder()

    @property
    def render_pipeline(self) -> wgpu.GPURenderPipeline:
        return self._render_pipeline

    def prepare(self, 
        device: wgpu.GPUDevice, 
        render_texture_format: str, 
        scene: Scene,
        frame_data: PerFrameData
    ) -> None:
        pc = OverlayPipelineConfiguration()
        self._render_pipeline = self._builder.build(
            device, 
            render_texture_format, 
            scene, 
            pc,
            frame_data
        )

    def render(
        self, 
        render_pass: wgpu.GPURenderPassEncoder, 
        frame_data: PerFrameData, 
        scene: Scene) -> None:
        render_pass.set_bind_group(
            0, 
            frame_data.overlay_bind_groups[OverlayBindGroups.VIEWPORT], 
            [], 
            0, 
            99999)
        render_pass.draw(
            vertex_count=6, 
            instance_count=1,
            first_vertex=0, 
            first_instance=0
        )

@dataclass(init=False)
class OverlayPipelineConfiguration:
    """
    Simple data class used to group the various pipeline aspects.
    Intended to only be used inside of a renderer.
    """
    render_texture_format: str
    shader: wgpu.GPUShaderModule
    vertex_config: dict
    fragment_config: dict
    viewport_bind_group_layout: wgpu.GPUBindGroupLayout


class OverlayBuilder:
    def __init__(self) -> None:
        self._rendering_pipeline: wgpu.GPURenderPipeline

    def build(
        self,
        device: wgpu.GPUDevice,
        render_texture_format: str,
        scene: Scene,
        pc: OverlayPipelineConfiguration,
        frame_data: PerFrameData
    ) -> wgpu.GPURenderPipeline:
        self._load_shaders(device, pc)
        self._build_pipeline_configuration(render_texture_format, pc)
        self._setup_uniform_bind_groups(device, scene, pc, frame_data)
        self._rendering_pipeline = self._setup_renderer_pipeline(device, pc)
        self._create_bind_groups(device, scene, pc, frame_data)
        self._load_uniform_buffers(device, scene, pc)
        return self._rendering_pipeline
    
    def _load_shaders(
        self, device: wgpu.GPUDevice, pc: OverlayPipelineConfiguration
    ) -> None:
        shader_path = os.path.join(
            Path.cwd(), "agents_playground/gpu/shaders/overlay.wgsl"
        )
        pc.shader = load_shader(shader_path, "Overlay Shader", device)
    
    def _build_pipeline_configuration(
        self,
        render_texture_format: str,
        pc: OverlayPipelineConfiguration,
    ) -> None: 
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

    def _setup_uniform_bind_groups(
        self,
        device: wgpu.GPUDevice,
        scene: Scene,
        pc: OverlayPipelineConfiguration,
        frame_data: PerFrameData
    ) -> None: 
        # TODO: This sort of thing should be handled with a Maybe.
        if OverlayBufferNames.VIEWPORT not in frame_data.overlay_buffers:
            frame_data.overlay_buffers[OverlayBufferNames.VIEWPORT] = device.create_buffer(
                label="Viewport Buffer",
                size=8, # Width (i32) + Height (i32)
                usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,  # type: ignore
            )

        pc.viewport_bind_group_layout = device.create_bind_group_layout(
            label = "Overlay Viewport Bind Group Layout",
            entries = [
                {
                    "binding": 0,
                    "visibility": wgpu.flags.ShaderStage.VERTEX | wgpu.flags.ShaderStage.FRAGMENT,  # type: ignore
                    "buffer": {"type": wgpu.BufferBindingType.uniform},  # type: ignore
                }
            ]
        )

    def _setup_renderer_pipeline(
        self,
        device: wgpu.GPUDevice,
        pc: OverlayPipelineConfiguration
    ) -> wgpu.GPURenderPipeline: 
        pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(
            label="Overlay Render Pipeline Layout",
            bind_group_layouts=[
                pc.viewport_bind_group_layout # type: ignore
            ]
        )

        depth_stencil_config = {
            "format": wgpu.enums.TextureFormat.depth24plus_stencil8,  # type: ignore
            "depth_write_enabled": True,
            "depth_compare": wgpu.enums.CompareFunction.less,  # type: ignore
        }

        return device.create_render_pipeline(
            label="Overlay Rendering Pipeline",
            layout=pipeline_layout,
            vertex=pc.vertex_config,
            fragment=pc.fragment_config,
            depth_stencil=depth_stencil_config,
            multisample=None
        ) 

    def _create_bind_groups(
        self,
        device: wgpu.GPUDevice,
        scene: Scene,
        pc: OverlayPipelineConfiguration,
        frame_data: PerFrameData
    ) -> None:
        frame_data.overlay_bind_groups[OverlayBindGroups.VIEWPORT] = device.create_bind_group(
            label="Overlay Viewport Bind Group",
            layout=pc.viewport_bind_group_layout,
            entries=[
                {
                    "binding": 0,
                    "resource": {
                        "buffer": frame_data.overlay_buffers[OverlayBufferNames.VIEWPORT],
                        "offset": 0,
                        "size": frame_data.overlay_buffers[OverlayBufferNames.VIEWPORT].size,
                    },
                }
            ],
        )
        

    def _load_uniform_buffers(
        self,
        device: wgpu.GPUDevice,
        scene: Scene,
        pc: OverlayPipelineConfiguration
    ) -> None: 
        pass
