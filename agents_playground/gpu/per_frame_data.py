from dataclasses import dataclass

import wgpu
import wgpu.backends.wgpu_native

@dataclass(init=False)
class PerFrameData:
  """
  Data class for grouping the things that can be updated by the client.
  """
  camera_buffer: wgpu.GPUBuffer
  vbo: wgpu.GPUBuffer
  ibo: wgpu.GPUBuffer
  vertex_normals_buffer: wgpu.GPUBuffer
  model_world_transform_buffer: wgpu.GPUBuffer
  display_config_buffer: wgpu.GPUBuffer
  num_primitives: int
  render_pipeline: wgpu.GPURenderPipeline
  camera_bind_group: wgpu.GPUBindGroup
  model_transform_bind_group: wgpu.GPUBindGroup
  display_config_bind_group: wgpu.GPUBindGroup