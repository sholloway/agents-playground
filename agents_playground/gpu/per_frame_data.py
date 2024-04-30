from dataclasses import dataclass

import wgpu
import wgpu.backends.wgpu_native

@dataclass(init=False)
class PerFrameData:
  """
  Data class for grouping the things that can be updated by the client.
  """
  # Scene
  model_world_transform_buffer: wgpu.GPUBuffer | None = None
  display_config_buffer: wgpu.GPUBuffer
  display_config_bind_group: wgpu.GPUBindGroup

  # Camera
  camera_buffer: wgpu.GPUBuffer | None = None

  # Landscape Stuff
  landscape_num_primitives: int
  landscape_camera_bind_group: wgpu.GPUBindGroup
  landscape_model_transform_bind_group: wgpu.GPUBindGroup

  # Normals Rendering Stuff
  normals_num_primitives: int
  normals_camera_bind_group: wgpu.GPUBindGroup
  normals_model_transform_bind_group: wgpu.GPUBindGroup

  # Agents
  


  def __repr__(self) -> str:
    msg = f"""
    PerFrameData
    Number of Primitives: {self.landscape_num_primitives}
    Camera Buffer {self.camera_buffer}
    Model/World Transform Buffer {self.model_world_transform_buffer}
    Display Config Buffer {self.display_config_buffer}
    """
    return msg