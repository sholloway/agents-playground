import wgpu
from wgpu import GPURenderPassEncoder, GPURenderPipeline
import wgpu.backends.wgpu_native

from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.spatial.mesh import MeshBuffer, MeshData

class LandscapeRenderer(GPURenderer):
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
        render_pass.set_bind_group(0, vertex_buffer.bind_groups[0], [], 0, 99999)
        render_pass.set_bind_group(1, vertex_buffer.bind_groups[1], [], 0, 99999)
        render_pass.set_bind_group(2, vertex_buffer.bind_groups[2], [], 0, 99999)

        render_pass.set_vertex_buffer(
            slot=0, buffer=mesh_data.vertex_buffer.unwrap().vbo
        )

        render_pass.set_index_buffer(
            buffer=mesh_data.vertex_buffer.unwrap().ibo,
            index_format=wgpu.IndexFormat.uint32,  # type: ignore
        )

        render_pass.draw_indexed(
            index_count=vertex_buffer.count,
            instance_count=1,
            first_index=0,
            base_vertex=0,
            first_instance=0,
        )
