from array import array as create_array
from typing import Dict, List

import wgpu
import wgpu.backends.wgpu_native

class NormalsMeshConfigurationBuilder:
  def configure_pipeline_primitives(self) -> Dict:
    """
    Specify what type of geometry should the GPU render.
    Returns a structs.PrimitiveState
    """
    primitive_config = {
      "topology":   wgpu.PrimitiveTopology.line_list, # type: ignore
    }
    return primitive_config

  def create_vertex_buffer(self, device: wgpu.GPUDevice, vertices: List[float]) -> wgpu.GPUBuffer:
    vbo_data = create_array('f', vertices)
    return device.create_buffer_with_data(
      label = 'Vertex Buffer',
      data  = vbo_data,
      usage = wgpu.BufferUsage.VERTEX # type: ignore
    )

  def create_index_buffer(
    self,
    device: wgpu.GPUDevice,
    indices: List[int]
  )-> wgpu.GPUBuffer:
    ibo_data = create_array('I', indices)
    return device.create_buffer_with_data(
      label = 'Index Buffer',
      data  = ibo_data,
      usage = wgpu.BufferUsage.INDEX # type: ignore
    )