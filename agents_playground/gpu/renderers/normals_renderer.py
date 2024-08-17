from abc import abstractmethod

import wgpu
import wgpu.backends.wgpu_native
from agents_playground.cameras.camera import Camera
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.normals_renderer_builder import (
    NormalsRendererBuilder,
)
from agents_playground.gpu.renderer_builders.renderer_builder import RendererBuilder

from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.scene import Scene
from agents_playground.simulation.context import SimulationContextBuilder
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.mesh import MeshBuffer, MeshData


class NormalsRenderer(GPURenderer):
    def __init__(self, builder: RendererBuilder | None = None) -> None:
        self._render_pipeline: wgpu.GPURenderPipeline
        self.builder = NormalsRendererBuilder() if builder is None else builder

    @property
    def render_pipeline(self) -> wgpu.GPURenderPipeline:
        return self._render_pipeline

    def prepare(
        self,
        sim_context_builder: SimulationContextBuilder
    ) -> None:
        pc = PipelineConfiguration()
        self._render_pipeline = self.builder.build(sim_context_builder, pc)

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
