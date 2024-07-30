import os
from pathlib import Path
import wgpu
import wgpu.backends.wgpu_native

from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.shaders import load_shader
from agents_playground.scene import Scene

"""
For now, just get an overlay that is a solid color that is constrained to a fixed space.
"""
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
        scene: Scene
    ) -> None:
        pc = PipelineConfiguration()
        self._render_pipeline = self._builder.build(
            device, 
            render_texture_format, 
            scene, 
            pc
        )

    def render(self, render_pass: wgpu.GPURenderPassEncoder) -> None:
        render_pass.draw(
            vertex_count=6, 
            instance_count=1,
            first_vertex=0, 
            first_instance=0
        )

class OverlayBuilder:
    def __init__(self) -> None:
        self._rendering_pipeline: wgpu.GPURenderPipeline

    def build(
        self,
        device: wgpu.GPUDevice,
        render_texture_format: str,
        scene: Scene,
        pc: PipelineConfiguration
    ) -> wgpu.GPURenderPipeline:
        self._load_shaders(device, pc)
        self._build_pipeline_configuration(render_texture_format, pc)
        self._setup_uniform_bind_groups(device, scene, pc)
        self._rendering_pipeline = self._setup_renderer_pipeline(device, pc)
        self._create_bind_groups(device, scene, pc)
        self._load_uniform_buffers(device, scene, pc)
        return self._rendering_pipeline
    
    def _load_shaders(
        self, device: wgpu.GPUDevice, pc: PipelineConfiguration
    ) -> None:
        shader_path = os.path.join(
            Path.cwd(), "agents_playground/gpu/shaders/overlay.wgsl"
        )
        pc.shader = load_shader(shader_path, "Overlay Shader", device)
    
    def _build_pipeline_configuration(
        self,
        render_texture_format: str,
        pc: PipelineConfiguration,
    ) -> None: 
        pc.primitive_config = {}
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
        pc: PipelineConfiguration
    ) -> None: 
        pass

    def _setup_renderer_pipeline(
        self,
        device: wgpu.GPUDevice,
        pc: PipelineConfiguration
    ) -> wgpu.GPURenderPipeline: 
        pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(
            label="Overlay Render Pipeline Layout",
            bind_group_layouts=[]
        )

        depth_stencil_config = {
            "format": wgpu.enums.TextureFormat.depth24plus_stencil8,  # type: ignore
            "depth_write_enabled": True,
            "depth_compare": wgpu.enums.CompareFunction.less,  # type: ignore
        }

        return device.create_render_pipeline(
            label="Overlay Rendering Pipeline",
            layout=pipeline_layout,
            primitive=pc.primitive_config,
            vertex=pc.vertex_config,
            fragment=pc.fragment_config,
            depth_stencil=depth_stencil_config,
            multisample=None
        ) 

    def _create_bind_groups(
        self,
        device: wgpu.GPUDevice,
        scene: Scene,
        pc: PipelineConfiguration
    ) -> None: 
        pass

    def _load_uniform_buffers(
        self,
        device: wgpu.GPUDevice,
        scene: Scene,
        pc: PipelineConfiguration
    ) -> None: 
        pass
