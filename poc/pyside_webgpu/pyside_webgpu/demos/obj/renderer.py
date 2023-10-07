"""
A module that provides a rendering pipeline for rendering a 3D mesh.
"""

from typing import Protocol
from pyside_webgpu.demos.obj.frame_data import PerFrameData

import wgpu
import wgpu.backends.rs

from agents_playground.cameras.camera import Camera3d

from agents_playground.loaders.obj_loader import TriangleMesh
from agents_playground.spatial.matrix import Matrix

class GPURenderer(Protocol):
  def prepare(
    self, 
    device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh: TriangleMesh, 
    camera: Camera3d,
    model_world_transform: Matrix
  ) -> PerFrameData:
    ...

  def render(
    self, 
    render_pass: wgpu.GPURenderPassEncoder, 
    frame_data: PerFrameData
  ) -> None:
    ...