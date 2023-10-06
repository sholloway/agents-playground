"""
A module that provides a rendering pipeline for rendering a 3D mesh.
"""
from abc import abstractmethod

from typing import Protocol

import wgpu
import wgpu.backends.rs

from agents_playground.cameras.camera import Camera3d
from agents_playground.loaders.obj_loader import TriangleMesh
from agents_playground.spatial.matrix import Matrix

from pyside_webgpu.demos.obj.frame_data import PerFrameData
from pyside_webgpu.demos.obj.pipeline_configuration import PipelineConfiguration

class RendererBuilder(Protocol):
  def build(self, device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh: TriangleMesh, 
    camera: Camera3d,
    model_world_transform: Matrix,
    pc: PipelineConfiguration,
    frame_data: PerFrameData
  ) -> PerFrameData:
    self.load_shaders(device, pc)
    self.build_pipeline_configuration(render_texture_format, pc)
    self.load_mesh(device, mesh, frame_data)
    self.setup_camera(device, camera, pc, frame_data)
    self.setup_model_transform(device, model_world_transform, pc, frame_data)
    self.setup_uniform_bind_groups(device, pc)
    self.setup_renderer_pipeline(device, pc, frame_data)
    self.create_bind_groups(device, pc, frame_data)
    self.load_uniform_buffers(device, pc, frame_data)
    return frame_data
  
  @abstractmethod
  def load_shaders(self, device: wgpu.GPUDevice, pc: PipelineConfiguration) -> None:
    ...

  @abstractmethod
  def build_pipeline_configuration(
    self, 
    render_texture_format: str,
    pc: PipelineConfiguration,
  ) -> None:
    ...

  @abstractmethod
  def load_mesh(
    self, 
    device: wgpu.GPUDevice, 
    mesh: TriangleMesh, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def setup_camera(
    self, 
    device: wgpu.GPUDevice, 
    camera: Camera3d, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def setup_model_transform(
    self,
    device: wgpu.GPUDevice, 
    model_world_transform: Matrix, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def setup_uniform_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration
  ) -> None:
    ...

  @abstractmethod
  def setup_renderer_pipeline(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def create_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def load_uniform_buffers(
    self,
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...