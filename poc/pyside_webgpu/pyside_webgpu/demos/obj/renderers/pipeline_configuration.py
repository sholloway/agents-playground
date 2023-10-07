from array import ArrayType
from dataclasses import dataclass
from typing import Dict
import wgpu
import wgpu.backends.rs

@dataclass(init=False)
class PipelineConfiguration:
  """
  Simple data class used to group the various pipeline aspects.
  Intended to only be used inside of a renderer.
  """
  render_texture_format: str
  white_model_shader: wgpu.GPUShaderModule
  primitive_config: Dict
  vertex_config: Dict
  fragment_config: Dict
  camera_data: ArrayType
  model_world_transform_data: ArrayType
  camera_uniform_bind_group_layout: wgpu.GPUBindGroupLayout
  model_uniform_bind_group_layout: wgpu.GPUBindGroupLayout