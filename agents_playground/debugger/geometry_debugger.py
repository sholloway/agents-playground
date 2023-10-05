"""
A module that provides a rendering pipeline for diagnosing 3D meshes.
"""

from dataclasses import dataclass
import wgpu
import wgpu.backends.rs

@dataclass
class PerFrameData:
  pass

class GeometryDebugger:
  def __init__(self) -> None:
    pass

  def prepare(self, device: wgpu.GPUDevice, mesh_data) -> PerFrameData:
    ...

  def render(self, frame_data:PerFrameData) -> None:
    pass

