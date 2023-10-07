import os
from pathlib import Path

from pyside_webgpu.demos.obj.renderers.pipeline_configuration import PipelineConfiguration
from pyside_webgpu.demos.obj.renderers.renderer_builder import RendererBuilder
from pyside_webgpu.demos.obj.utilities import load_shader

import wgpu
import wgpu.backends.rs

class EdgeRendererBuilder(RendererBuilder):
  def __init__(self) -> None:
    super().__init__()

  def _load_shaders(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration
  ) -> None:
    shader_path = os.path.join(Path.cwd(), 'poc/pyside_webgpu/pyside_webgpu/demos/obj/shaders/triangle_edge.wgsl')
    pc.white_model_shader = load_shader(shader_path, 'Triangle Edge Shader', device)