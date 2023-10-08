from agents_playground.cameras.camera import Camera3d
from agents_playground.loaders.obj_loader import Mesh, TriangleMesh
from agents_playground.spatial.matrix import Matrix

from pyside_webgpu.demos.obj.renderers.edge.edge_renderer_builder import EdgeRendererBuilder
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
    self.builder = EdgeRendererBuilder() if builder is None else builder

  def prepare(
    self, 
    device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh: Mesh, 
    camera: Camera3d,
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
    raise NotImplementedError('TODO...')