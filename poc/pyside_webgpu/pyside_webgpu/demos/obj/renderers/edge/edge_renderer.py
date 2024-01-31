from agents_playground.spatial.mesh import MeshBuffer
from pyside_webgpu.demos.obj.renderers.edge.edge_renderer_builder import EdgeRendererConfigurationBuilder
from agents_playground.cameras.camera import Camera
from agents_playground.spatial.matrix.matrix import Matrix

from pyside_webgpu.demos.obj.renderers.frame_data import PerFrameData
from pyside_webgpu.demos.obj.renderers.pipeline_configuration import PipelineConfiguration
from pyside_webgpu.demos.obj.renderers.renderer import GPURenderer
from pyside_webgpu.demos.obj.renderers.renderer_builder import RendererBuilder

import wgpu
import wgpu.backends.rs

class EdgeRenderer(GPURenderer):
  """
  A mesh renderer that draws the edges of a mesh.
  """
  def __init__(self, builder: RendererBuilder | None = None) -> None:
    self.builder = EdgeRendererConfigurationBuilder() if builder is None else builder

  def prepare(
    self, 
    device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh: MeshBuffer, 
    camera: Camera,
    model_world_transform: Matrix
  ) -> PerFrameData:
    pc = PipelineConfiguration()
    frame_data = PerFrameData()
    return self.builder.build(
      device, 
      render_texture_format, 
      mesh, 
      camera, 
      model_world_transform, 
      pc, 
      frame_data
    )
  
  def render(
    self, 
    render_pass: wgpu.GPURenderPassEncoder, 
    frame_data: PerFrameData
  ) -> None:
    render_pass.set_bind_group(0, frame_data.camera_bind_group, [], 0, 99999)
    render_pass.set_bind_group(1, frame_data.model_transform_bind_group, [], 0, 99999)
    render_pass.set_vertex_buffer(slot = 0, buffer = frame_data.vbo)
    render_pass.set_index_buffer(buffer = frame_data.ibo, index_format=wgpu.IndexFormat.uint32) # type: ignore

    render_pass.draw_indexed(
      index_count    = frame_data.num_primitives, 
      instance_count = 1, 
      first_index    = 0, 
      base_vertex    = 0, 
      first_instance = 0
    )