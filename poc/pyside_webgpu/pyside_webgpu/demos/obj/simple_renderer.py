from agents_playground.cameras.camera import Camera3d
from agents_playground.loaders.obj_loader import TriangleMesh
from agents_playground.spatial.matrix import Matrix

from pyside_webgpu.demos.obj.frame_data import PerFrameData
from pyside_webgpu.demos.obj.pipeline_configuration import PipelineConfiguration
from pyside_webgpu.demos.obj.renderer import GPURenderer
from pyside_webgpu.demos.obj.renderer_builder import RendererBuilder
from pyside_webgpu.demos.obj.simple_renderer_builder import SimpleRendererBuilder

import wgpu
import wgpu.backends.rs

class SimpleRenderer(GPURenderer):
  def __init__(self, builder: RendererBuilder | None = None) -> None:
    self.builder = SimpleRendererBuilder() if builder is None else builder

  def prepare(
    self, 
    device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh: TriangleMesh, 
    camera: Camera3d,
    model_world_transform: Matrix
  ) -> PerFrameData:
    pc = PipelineConfiguration()
    frame_data = PerFrameData()
    return self.builder.build(
      device, 
      render_texture_format, 
      mesh, camera, 
      model_world_transform, 
      pc, 
      frame_data
    )

  def render(self, render_pass: wgpu.GPURenderPassEncoder, frame_data: PerFrameData) -> None:
    render_pass.set_bind_group(0, frame_data.camera_bind_group, [], 0, 99999)
    render_pass.set_bind_group(1, frame_data.model_transform_bind_group, [], 0, 99999)
    render_pass.set_vertex_buffer(slot = 0, buffer = frame_data.vbo)
    render_pass.set_vertex_buffer(slot = 1, buffer = frame_data.vertex_normals_buffer)
    render_pass.set_index_buffer(buffer = frame_data.ibo, index_format=wgpu.IndexFormat.uint32) # type: ignore

    render_pass.draw_indexed(
      index_count    = frame_data.num_triangles, 
      instance_count = 1, 
      first_index    = 0, 
      base_vertex    = 0, 
      first_instance = 0
    )  