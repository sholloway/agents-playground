from dataclasses import dataclass, field
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
    CONFIG = 1

class OverlayBufferNames(StrEnum):
    VIEWPORT = "viewport_buffer"
    CONFIG = 'overlay_config_buffer'

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
        render_pass.set_bind_group(
            1, 
            frame_data.overlay_bind_groups[OverlayBindGroups.CONFIG], 
            [], 
            0, 
            99999)
        render_pass.draw(
            vertex_count=6, 
            instance_count=1,
            first_vertex=0, 
            first_instance=0
        )

@dataclass
class OverlayPipelineConfiguration:
    """
    Simple data class used to group the various pipeline aspects.
    Intended to only be used inside of a renderer.
    """
    render_texture_format: str = 'NOT SET'
    vertex_config: dict = field(default_factory=dict)
    fragment_config: dict = field(default_factory=dict)
    bind_group_layouts: dict[str, wgpu.GPUBindGroupLayout] = field(default_factory=dict)
    shader: wgpu.GPUShaderModule | None = None


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
        self._setup_viewport_buffers(device, pc, frame_data)
        self._setup_overlay_config_buffers(device, pc, frame_data)

    def _setup_viewport_buffers(self, device: wgpu.GPUDevice, pc: OverlayPipelineConfiguration, frame_data: PerFrameData):
        if OverlayBufferNames.VIEWPORT not in frame_data.overlay_buffers:
            frame_data.overlay_buffers[OverlayBufferNames.VIEWPORT] = device.create_buffer(
                label="Viewport Buffer",
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
    
    def _setup_overlay_config_buffers(self, device: wgpu.GPUDevice, pc: OverlayPipelineConfiguration, frame_data: PerFrameData):
        if OverlayBufferNames.CONFIG not in frame_data.overlay_buffers:
            frame_data.overlay_buffers[OverlayBufferNames.CONFIG] = device.create_buffer(
                label="Overlay Configuration Buffer",
                size=4 + 4 + 4 + 4 + 4 * 4 + 4 * 4, # loc_x (f32) + loc_y (f32) + Width (f32) + Height (f32) + background_color (vec4<f32>) + foreground_color(vec4<f32>)
                usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,  # type: ignore
            )

        pc.bind_group_layouts['overlay_config_bind_group_layout'] = device.create_bind_group_layout(
            label = "Overlay Configuration Bind Group Layout",
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
                pc.bind_group_layouts['viewport_bind_group_layout'], 
                pc.bind_group_layouts['overlay_config_bind_group_layout']
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
        self._create_viewport_bind_groups(device, pc, frame_data)
        self._create_overlay_config_bind_groups(device, pc, frame_data)
        
    def _create_viewport_bind_groups(
        self, 
        device: wgpu.GPUDevice, 
        pc: OverlayPipelineConfiguration,
        frame_data: PerFrameData
    ) -> None:
        frame_data.overlay_bind_groups[OverlayBindGroups.VIEWPORT] = device.create_bind_group(
            label="Overlay Viewport Bind Group",
            layout=pc.bind_group_layouts['viewport_bind_group_layout'],
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
    
    def _create_overlay_config_bind_groups(
        self, 
        device: wgpu.GPUDevice, 
        pc: OverlayPipelineConfiguration,
        frame_data: PerFrameData
    ) -> None:
        frame_data.overlay_bind_groups[OverlayBindGroups.CONFIG] = device.create_bind_group(
            label="Overlay Configuration Bind Group",
            layout=pc.bind_group_layouts['overlay_config_bind_group_layout'],
            entries=[
                {
                    "binding": 0,
                    "resource": {
                        "buffer": frame_data.overlay_buffers[OverlayBufferNames.CONFIG],
                        "offset": 0,
                        "size": frame_data.overlay_buffers[OverlayBufferNames.CONFIG].size,
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
