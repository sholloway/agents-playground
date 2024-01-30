
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline

class ScenePipeline(WebGpuPipeline):
  """
  Creates a WebGPU Rendering Pipeline that can render a Simulation Scene.
  """
  def __init__(self) -> None:
    super().__init__()
  
  def initialize_pipeline(self, canvas: WgpuWidget) -> None:
    ...

  
  def refresh_aspect_ratio(self, aspect_ratio: float) -> None:
    ...
