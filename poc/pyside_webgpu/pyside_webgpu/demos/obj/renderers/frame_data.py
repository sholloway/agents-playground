from dataclasses import dataclass
import wgpu
import wgpu.backends.rs

@dataclass(init=False)
class PerFrameData:
  """
  Data class for grouping the things that can be updated by the client.
  """
  camera_buffer: wgpu.GPUBuffer
  vbo: wgpu.GPUBuffer
  vertex_normals_buffer: wgpu.GPUBuffer
  ibo: wgpu.GPUBuffer
  num_triangles: int
  model_world_transform_buffer: wgpu.GPUBuffer
  render_pipeline: wgpu.GPURenderPipeline
  camera_bind_group: wgpu.GPUBindGroup
  model_transform_bind_group: wgpu.GPUBindGroup