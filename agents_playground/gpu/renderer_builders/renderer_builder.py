from abc import abstractmethod
from typing import Protocol

import wgpu
import wgpu.backends.wgpu_native
from agents_playground.cameras.camera import Camera
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration


from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.mesh import MeshBuffer

class RendererBuilder(Protocol):
  def build(self, device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh: MeshBuffer, 
    camera: Camera,
    model_world_transform: Matrix,
    pc: PipelineConfiguration,
    frame_data: PerFrameData
  ) -> PerFrameData:
    self._load_shaders(device, pc)
    self._build_pipeline_configuration(render_texture_format, pc)
    self._load_mesh(device, mesh, frame_data)
    self._setup_camera(device, camera, pc, frame_data)
    self._setup_model_transform(device, model_world_transform, pc, frame_data)
    self._setup_uniform_bind_groups(device, pc, frame_data)
    self._setup_renderer_pipeline(device, pc, frame_data)
    self._create_bind_groups(device, pc, frame_data)
    self._load_uniform_buffers(device, pc, frame_data)
    return frame_data
  
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
    mesh: MeshBuffer, 
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
  ) -> None:
    ...

  @abstractmethod
  def _create_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
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