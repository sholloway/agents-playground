from abc import ABC, abstractmethod
from array import array as create_array
from array import ArrayType

import wgpu
import wgpu.backends.wgpu_native
from agents_playground.cameras.camera import Camera
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration


from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.mesh import MeshBuffer, MeshData

def assemble_camera_data(camera: Camera) -> ArrayType:
  view_matrix = camera.view_matrix
  proj_matrix = camera.projection_matrix
  proj_view: tuple = \
    proj_matrix.transpose().flatten(MatrixOrder.Row) + \
    view_matrix.flatten(MatrixOrder.Row)
  return create_array('f', proj_view)

class RendererBuilder(ABC):
  """
  Responsible for building a renderer pipeline.
  """
  def __init__(self) -> None:
    super().__init__()
    self._rendering_pipeline: wgpu.GPURenderPipeline

  def build(self, device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh_data: MeshData, 
    camera: Camera,
    model_world_transform: Matrix,
    pc: PipelineConfiguration,
    frame_data: PerFrameData, 
  ) -> wgpu.GPURenderPipeline:
    self._load_shaders(device, pc)
    self._build_pipeline_configuration(render_texture_format, pc)
    self._load_mesh(device, mesh_data, frame_data)
    self._setup_camera(device, camera, pc, frame_data)
    self._setup_model_transform(device, model_world_transform, pc, frame_data)
    self._setup_uniform_bind_groups(device, pc, frame_data)
    self._rendering_pipeline = self._setup_renderer_pipeline(device, pc, frame_data)
    self._create_bind_groups(device, pc, frame_data, mesh_data)
    self._load_uniform_buffers(device, pc, frame_data)
    return self._rendering_pipeline
  
  @abstractmethod
  def _load_shaders(self, device: wgpu.GPUDevice, pc: PipelineConfiguration) -> None:
    ...

  @abstractmethod
  def _build_pipeline_configuration(
    self, 
    render_texture_format: str,
    pc: PipelineConfiguration,
  ) -> None:
    ...

  @abstractmethod
  def _load_mesh(
    self, 
    device: wgpu.GPUDevice, 
    mesh_data: MeshData, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _setup_camera(
    self, 
    device: wgpu.GPUDevice, 
    camera: Camera, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _setup_model_transform(
    self,
    device: wgpu.GPUDevice, 
    model_world_transform: Matrix, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _setup_uniform_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration,
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _setup_renderer_pipeline(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> wgpu.GPURenderPipeline:
    ...

  @abstractmethod
  def _create_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData,
    mesh_data: MeshData
  ) -> None:
    ...

  @abstractmethod
  def _load_uniform_buffers(
    self,
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...