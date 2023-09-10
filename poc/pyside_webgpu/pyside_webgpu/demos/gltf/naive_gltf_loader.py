"""
This module is a simple implementation of a model viewer that 
can load glTF models.

To Run
poetry run python -X dev pyside_webgpu/demos/gltf/naive_gltf_loader.py
"""
from functools import partial
import os
from pathlib import Path

from pygltflib import GLTF2
import wx

import wgpu
import wgpu.backends.rs

from pyside_webgpu.demos.gltf.ui import AppWindow

"""
TODO
- [X] Select a glTF parser.
- [X] Select a few glTF models.
- Implement this beast!
"""

def select_scene() -> str:
  scene_dir = 'pyside_webgpu/demos/pyside/models/glTF'
  scene_filename = 'Box.gltf'
  return os.path.join(Path.cwd(), scene_dir, scene_filename)

def load_scene(scene_file_path: str) -> GLTF2:
  gltf = GLTF2().load(scene_file_path)
  if gltf is not None:
    return gltf  
  else:
    raise Exception(f'The file {scene_file_path} was not able to be loaded.')
  
def provision_adapter(canvas: wgpu.gui.WgpuCanvasInterface) -> wgpu.GPUAdapter:
  return wgpu.request_adapter( # type: ignore
    canvas=canvas, 
    power_preference='high-performance'
  ) 

def provision_gpu_device(adapter: wgpu.GPUAdapter) -> wgpu.GPUDevice:
  return adapter.request_device(
    label='only-gpu-device', 
    required_features=[],
    required_limits={}, 
    default_queue={}
  )

def load_shader(shader_path: str, name: str, device: wgpu.GPUDevice) -> wgpu.GPUShaderModule:
  with open(file = shader_path, mode = 'r') as filereader:
    shader_code = filereader.read()
  return device.create_shader_module(
    label = name,
    code  = shader_code
  )

def build_render_pipeline(
  canvas_context: wgpu.GPUCanvasContext, 
  device: wgpu.GPUDevice
) -> wgpu.GPURenderPipeline:
  # Load the shaders
  vert_shader_path = os.path.join(Path.cwd(), 'pyside_webgpu/demos/gltf/simple_shader.vert.wgsl')
  frag_shader_path = os.path.join(Path.cwd(), 'pyside_webgpu/demos/gltf/simple_shader.frag.wgsl')
  vert_shader: wgpu.GPUShaderModule = load_shader(vert_shader_path, 'vert_shader', device)
  frag_shader: wgpu.GPUShaderModule = load_shader(frag_shader_path, 'frag_shader', device)

  # No bind group and layout, we should not create empty ones.
  pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(bind_group_layouts=[])

  # Not really sure what this is doing at the moment.
  render_texture_format = canvas_context.get_preferred_format(device.adapter)
  canvas_context.configure(device=device, format=render_texture_format)

  # structs.PrimitiveState
  # Specify what type of geometry should the GPU render.
  primitive_config={
    "topology": wgpu.PrimitiveTopology.triangle_list, # type: ignore
    "front_face": wgpu.FrontFace.ccw, # type: ignore
    "cull_mode": wgpu.CullMode.none, # type: ignore
  }

  # structs.VertexState
  # Configure the vertex shader.
  vertex_config = {
    "module": vert_shader,
    "entry_point": "vs_main",
    "buffers": [],
  }

  # structs.FragmentState
  # Configure the fragment shader.
  fragment_config = {
    "module": frag_shader,
    "entry_point": "fs_main",
    "targets": [
      {
        "format": render_texture_format,
        "blend": {
          "color": (
            wgpu.BlendFactor.one,   # type: ignore
            wgpu.BlendFactor.zero,  # type: ignore
            wgpu.BlendOperation.add # type: ignore
          ),
          "alpha": (
            wgpu.BlendFactor.one,   # type: ignore
            wgpu.BlendFactor.zero,  # type: ignore
            wgpu.BlendOperation.add # type: ignore
          )
        }
      }
    ]
  }

  return device.create_render_pipeline(
    label         = 'Rendering Pipeline', 
    layout        = pipeline_layout,
    primitive     = primitive_config,
    vertex        = vertex_config,
    fragment      = fragment_config,
    depth_stencil = None,
    multisample   = None
  )

def draw_frame(
  canvas_context: wgpu.GPUCanvasContext, 
  device: wgpu.GPUDevice,
  render_pipeline: wgpu.GPURenderPipeline
):
  current_texture_view: wgpu.GPUCanvasContext = canvas_context.get_current_texture()
  command_encoder = device.create_command_encoder()

  # The first command to encode is the instruction to do a 
  # rendering pass.
  render_pass: wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
    color_attachments=[
      {
        "view": current_texture_view,
        "resolve_target": None,
        "clear_value": (0, 0, 0, 1),
        "load_op": wgpu.LoadOp.clear,  # type: ignore
        "store_op": wgpu.StoreOp.store # type: ignore
      }
    ],
  )

  # Associate the render pipeline with the GPURenderPassEncoder.
  render_pass.set_pipeline(render_pipeline)
  
  # Draw primitives based on the vertex buffers. 
  render_pass.draw(
    vertex_count = 3, 
    instance_count = 1, 
    first_vertex = 0, 
    first_instance = 0)
  
  render_pass.end()
  device.queue.submit([command_encoder.finish()])

def main() -> None:
  app = wx.App()
  app_window = AppWindow()
  scene_file_path = select_scene()
  scene_data: GLTF2 = load_scene(scene_file_path)

  adapter: wgpu.GPUAdapter = provision_adapter(app_window.canvas)
  device: wgpu.GPUDevice = provision_gpu_device(adapter)

  canvas_context: wgpu.GPUCanvasContext = app_window.canvas.get_context()
  render_pipeline = build_render_pipeline(canvas_context, device)

  bound_draw_frame = partial(draw_frame, canvas_context, device, render_pipeline)
  app_window.canvas.request_draw(bound_draw_frame)

  app.MainLoop()

if __name__ == '__main__':
  main()