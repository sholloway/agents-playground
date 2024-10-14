from dataclasses import dataclass, field
from enum import IntEnum
import wgpu
from wgpu import GPURenderPassEncoder, GPURenderPipeline

from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.spatial.mesh import MeshBuffer, MeshData


class TextRendererBindGroups(IntEnum):
    VIEWPORT = 0
    CONFIG = 1


class TextRenderer(GPURenderer):
    """
    A generic renderer that can render text to a screen.
    """

    def __init__(self, render_pipeline: GPURenderPipeline) -> None:
        super().__init__()
        self._render_pipeline = render_pipeline

    @property
    def render_pipeline(self) -> GPURenderPipeline:
        return self._render_pipeline

    def render(
        self,
        render_pass: GPURenderPassEncoder,
        mesh_data: MeshData,
    ) -> None:
        vertex_buffer: MeshBuffer = mesh_data.vertex_buffer.unwrap()
        render_pass.set_bind_group(
            0, vertex_buffer.bind_groups[TextRendererBindGroups.VIEWPORT], [], 0, 99999
        )
        render_pass.set_bind_group(
            1, vertex_buffer.bind_groups[TextRendererBindGroups.CONFIG], [], 0, 99999
        )
        render_pass.draw(
            vertex_count=6, instance_count=1, first_vertex=0, first_instance=0
        )


@dataclass
class TextRendererPipelineConfiguration:
    """
    Simple data class used to group the various pipeline aspects.
    Intended to only be used inside of a renderer.
    """

    render_texture_format: str = "NOT SET"
    vertex_config: dict = field(default_factory=dict)
    fragment_config: dict = field(default_factory=dict)
    bind_group_layouts: dict[str, wgpu.GPUBindGroupLayout] = field(default_factory=dict)
    shader: wgpu.GPUShaderModule | None = None
