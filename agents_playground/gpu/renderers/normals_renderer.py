from abc import abstractmethod

import wgpu
import wgpu.backends.wgpu_native
from agents_playground.cameras.camera import Camera
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.normals_renderer_builder import NormalsRendererBuilder
from agents_playground.gpu.renderer_builders.renderer_builder import RendererBuilder

from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.scene import Scene
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.mesh import MeshBuffer, MeshData

class NormalsRenderer(GPURenderer):
  def __init__(
    self, 
    builder: RendererBuilder | None = None
  ) -> None:
    self._render_pipeline: wgpu.GPURenderPipeline
    self.builder = NormalsRendererBuilder() if builder is None else builder
  
  @property
  def render_pipeline(self) -> wgpu.GPURenderPipeline:
    return self._render_pipeline
  
  def prepare(
    self, 
    device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh_data: MeshData, 
    scene: Scene,
    frame_data: PerFrameData
  ) -> PerFrameData:
    pc = PipelineConfiguration()
    self._render_pipeline = self.builder.build(
      device, 
      render_texture_format, 
      mesh_data, 
      scene, 
      pc, 
      frame_data
    )
    return frame_data
  
  def render(
    self, 
    render_pass: wgpu.GPURenderPassEncoder, 
    frame_data: PerFrameData,
    mesh_data: MeshData
  ) -> None:
    normals_buffer: MeshBuffer = mesh_data.normals_buffer.unwrap()
    render_pass.set_bind_group(0, normals_buffer.bind_groups[0], [], 0, 99999)
    render_pass.set_bind_group(1, normals_buffer.bind_groups[1], [], 0, 99999)
    
    render_pass.set_vertex_buffer(
      slot   = 0, 
      buffer = mesh_data.normals_buffer.unwrap().vbo
    )

    render_pass.set_index_buffer(
      buffer       = mesh_data.normals_buffer.unwrap().ibo, 
      index_format = wgpu.IndexFormat.uint32 # type: ignore
    ) 

    render_pass.draw_indexed(
      index_count    = frame_data.normals_num_primitives, 
      instance_count = 1, 
      first_index    = 0, 
      base_vertex    = 0, 
      first_instance = 0
    )  