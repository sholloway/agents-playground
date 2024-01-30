from abc import abstractmethod
from typing import Protocol

import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

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

  