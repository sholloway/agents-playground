import wgpu
import wgpu.backends.wgpu_native
from agents_playground.cameras.camera import Camera
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration

from agents_playground.gpu.renderer_builders.renderer_builder import RendererBuilder
from agents_playground.gpu.renderer_builders.landscape_renderer_builder import LandscapeRendererBuilder
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.mesh import MeshData

class LandscapeRenderer(GPURenderer):
  def __init__(self, builder: RendererBuilder | None = None) -> None:
    super().__init__()
    self._render_pipeline: wgpu.GPURenderPipeline
    self.builder = LandscapeRendererBuilder() if builder is None else builder

  @property
  def render_pipeline(self) -> wgpu.GPURenderPipeline:
    return self._render_pipeline
  
  def prepare(
    self, 
    device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh_data: MeshData, 
    camera: Camera,
    model_world_transform: Matrix,
    frame_data: PerFrameData
  ) -> PerFrameData:
    pc = PipelineConfiguration()
    self._render_pipeline = self.builder.build(
      device, 
      render_texture_format, 
      mesh_data, 
      camera, 
      model_world_transform, 
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
    render_pass.set_bind_group(0, frame_data.landscape_camera_bind_group, [], 0, 99999)
    render_pass.set_bind_group(1, frame_data.landscape_model_transform_bind_group, [], 0, 99999)
    render_pass.set_bind_group(2, frame_data.display_config_bind_group, [], 0, 99999)
    
    render_pass.set_vertex_buffer(
      slot   = 0, 
      buffer = mesh_data.vertex_buffer.unwrap().vbo
    )

    render_pass.set_index_buffer(
      buffer       = mesh_data.vertex_buffer.unwrap().ibo, 
      index_format = wgpu.IndexFormat.uint32 # type: ignore
    ) 

    render_pass.draw_indexed(
      index_count    = frame_data.landscape_num_primitives, 
      instance_count = 1, 
      first_index    = 0, 
      base_vertex    = 0, 
      first_instance = 0
    )  