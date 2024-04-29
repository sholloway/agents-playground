
import os
from pathlib import Path
import wgpu
import wgpu.backends.wgpu_native

from agents_playground.cameras.camera import Camera
from agents_playground.fp import Something
from agents_playground.gpu.camera_configuration.camera_configuration_builder import CameraConfigurationBuilder
from agents_playground.gpu.mesh_configuration.builders.triangle_list_mesh_configuration_builder import TriangleListMeshConfigurationBuilder
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.renderer_builder import RendererBuilder
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.shader_configuration.default_shader_configuration_builder import DefaultShaderConfigurationBuilder
from agents_playground.gpu.shaders import load_shader
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.mesh import MeshBuffer, MeshData

class AgentRendererBuilder(RendererBuilder):
  def __init__(self) -> None:
    super().__init__()
    self._camera_config = CameraConfigurationBuilder()
    self._shader_config = DefaultShaderConfigurationBuilder()
    self._mesh_config   = TriangleListMeshConfigurationBuilder('Agent')

  def _load_shaders(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration
  ) -> None:
    shader_path: str = os.path.join(Path.cwd(), 'agents_playground/gpu/shaders/agent.wgsl')
    pc.shader = load_shader(shader_path, 'Agent Triangle Shader', device)

  def _build_pipeline_configuration(
    self, 
    render_texture_format: str,
    pc: PipelineConfiguration,
  ) -> None:
    pc.primitive_config = self._mesh_config.configure_pipeline_primitives()
    pc.vertex_config = self._shader_config.configure_vertex_shader(pc.shader) 
    pc.fragment_config = self._shader_config.configure_fragment_shader(render_texture_format, pc.shader)

  def _load_mesh(
    self, 
    device: wgpu.GPUDevice, 
    mesh_data: MeshData, 
    frame_data: PerFrameData
  ) -> None:
    # Load the 3D mesh into a GPUVertexBuffer.
    vertex_buffer: MeshBuffer = mesh_data.vertex_buffer.unwrap()
    mesh_data.vbo = Something(self._mesh_config.create_vertex_buffer(device, vertex_buffer.data))
    mesh_data.ibo = Something(self._mesh_config.create_index_buffer(device, vertex_buffer.index))
    # frame_data.landscape_num_primitives = vertex_buffer.count

  def _setup_camera(
    self, 
    device: wgpu.GPUDevice, 
    camera: Camera, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  def _setup_model_transform(
    self,
    device: wgpu.GPUDevice, 
    model_world_transform: Matrix, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  def _setup_uniform_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration,
    frame_data: PerFrameData
  ) -> None:
    ...

  def _setup_renderer_pipeline(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  def _create_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  def _load_uniform_buffers(
    self,
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

class AgentRenderer(GPURenderer):
  def __init__(self, builder: RendererBuilder | None = None) -> None:
    super().__init__()
    self._render_pipeline: wgpu.GPURenderPipeline
    self.builder = AgentRendererBuilder() if builder is None else builder

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
    frame_data: PerFrameData
  ) -> None:
    ...