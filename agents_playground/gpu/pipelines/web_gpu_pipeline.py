from abc import abstractmethod
from typing import Protocol

import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget
from agents_playground.cameras.camera import Camera

from agents_playground.spatial.mesh import MeshBuffer

class WebGpuPipeline(Protocol):
  """
  Orchestrate the WebGPU components.
  """
  @abstractmethod
  def initialize_pipeline(self, canvas: WgpuWidget) -> None:
    ...

  @abstractmethod
  def refresh_aspect_ratio(self, aspect_ratio: float) -> None:
    ...

  @property
  @abstractmethod
  def mesh(self) -> MeshBuffer:
    ...
  
  @mesh.setter
  @abstractmethod
  def mesh(self, other: MeshBuffer) -> None:
    ...
  
  @property
  @abstractmethod
  def camera(self) -> Camera:
    ...
  
  @camera.setter
  @abstractmethod
  def camera(self, other: Camera) -> None:
    ...

  