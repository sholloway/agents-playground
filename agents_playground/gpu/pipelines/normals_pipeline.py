import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget
from agents_playground.cameras.camera import Camera

from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline
from agents_playground.spatial.mesh import MeshBuffer

class NormalsPipeline(WebGpuPipeline):
  def __init__(self) -> None:
    super().__init__()
    self._normals_edges: MeshBuffer
    self._camera: Camera

  @property
  def mesh(self) -> MeshBuffer:
    return self._normals_edges
  
  @mesh.setter
  def mesh(self, other: MeshBuffer) -> None:
    self._normals_edges = other

  @property
  def camera(self) -> Camera:
    return self._camera
  
  @camera.setter
  def camera(self, other: Camera) -> None:
    self._camera = other
  
  def initialize_pipeline(self, canvas: WgpuWidget) -> None:
    pass

  def refresh_aspect_ratio(self, aspect_ratio: float) -> None:
    raise NotImplemented("TODO: Implement NormalsPipeline.refresh_aspect_ratio")