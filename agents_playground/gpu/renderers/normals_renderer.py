from abc import abstractmethod

import wgpu
from wgpu import GPURenderPipeline
import wgpu.backends.wgpu_native

from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.simulation.simulation_context_builder import SimulationContextBuilder
from agents_playground.spatial.mesh import MeshBuffer, MeshData

class NormalsRenderer(GPURenderer):
    def __init__(self, render_pipeline: GPURenderPipeline) -> None:
        super().__init__()
        self._render_pipeline = render_pipeline

    @property
    def render_pipeline(self) -> wgpu.GPURenderPipeline:
        return self._render_pipeline

    def render(
        self,
        render_pass: wgpu.GPURenderPassEncoder,
        mesh_data: MeshData,
    ) -> None:
        normals_buffer: MeshBuffer = mesh_data.normals_buffer.unwrap()
        render_pass.set_bind_group(0, normals_buffer.bind_groups[0], [], 0, 99999)
        render_pass.set_bind_group(1, normals_buffer.bind_groups[1], [], 0, 99999)

        render_pass.set_vertex_buffer(
            slot=0, buffer=mesh_data.normals_buffer.unwrap().vbo
        )

        render_pass.set_index_buffer(
            buffer=mesh_data.normals_buffer.unwrap().ibo,
            index_format=wgpu.IndexFormat.uint32,  # type: ignore
        )

        render_pass.draw_indexed(
            index_count=normals_buffer.count,
            instance_count=1,
            first_index=0,
            base_vertex=0,
            first_instance=0,
        )
