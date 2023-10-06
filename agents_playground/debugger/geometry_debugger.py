"""
A module that provides a rendering pipeline for diagnosing 3D meshes.
"""

from dataclasses import dataclass
import wgpu
import wgpu.backends.rs

from agents_playground.loaders.obj_loader import TriangleMesh

@dataclass
class PerFrameData:
  pass

# class GeometryDebugger:
#   def __init__(self) -> None:
#     return

#   def prepare(
#     self, 
#     device: wgpu.GPUDevice, 
#     mesh_data: TriangleMesh
#   ) -> PerFrameData | None:
#     return 

#   def render(self, frame_data:PerFrameData) -> None:
#     return