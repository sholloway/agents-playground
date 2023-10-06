
from array import array as create_array, ArrayType

from typing import Tuple
import wgpu
import wgpu.backends.rs

from agents_playground.cameras.camera import Camera3d
from agents_playground.spatial.matrix import MatrixOrder

def load_shader(shader_path: str, name: str, device: wgpu.GPUDevice) -> wgpu.GPUShaderModule:
  with open(file = shader_path, mode = 'r') as filereader:
    shader_code = filereader.read()
  return device.create_shader_module(
    label = name,
    code  = shader_code
  )

def array_byte_size(a: ArrayType) -> int:
  """Finds the size, in bytes, of a given array."""
  return a.buffer_info()[1]*a.itemsize

def assemble_camera_data(camera: Camera3d) -> ArrayType:
  view_matrix = camera.to_view_matrix()
  proj_matrix = camera.projection_matrix
  proj_view: Tuple = \
    proj_matrix.flatten(MatrixOrder.Row) + \
    view_matrix.transpose().flatten(MatrixOrder.Row)
  return create_array('f', proj_view)