"""
This module is a simple implementation of a model viewer that 
can load Obj models.

To Run
poetry run python -X dev pyside_webgpu/demos/obj/app.py
"""
from agents_playground.loaders.obj_loader import ObjLoader, Obj

import os
from pathlib import Path

import wx
import wgpu
import wgpu.backends.rs

from pyside_webgpu.demos.obj.ui import AppWindow

def select_scene() -> str:
  """
  Find the path for the desired scene.
  """
  scene_dir = 'pyside_webgpu/demos/obj/models'
  scene_filename = 'skull.obj'
  return os.path.join(Path.cwd(), scene_dir, scene_filename)

def parse_scene_file(scene_file_path: str) -> Obj:
  return ObjLoader().load(scene_file_path)

def provision_adapter(canvas: wgpu.gui.WgpuCanvasInterface) -> wgpu.GPUAdapter:
  """
  Create a high performance GPUAdapter for a Canvas.
  """
  return wgpu.request_adapter( # type: ignore
    canvas=canvas, 
    power_preference='high-performance'
  ) 

def provision_gpu_device(adapter: wgpu.GPUAdapter) -> wgpu.GPUDevice:
  """
  Get an instance of the GPUDevice that is associated with a 
  provided GPUAdapter.
  """
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
  """
  Create the WebGPU Render Pipeline.
  """
  # Load the shaders
  vert_shader_path = os.path.join(Path.cwd(), 'pyside_webgpu/demos/obj/shaders/white_model.vert.wgsl')
  frag_shader_path = os.path.join(Path.cwd(), 'pyside_webgpu/demos/obj/shaders/white_model.frag.wgsl')
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
    "entry_point": "main",
    "buffers": [],
  }

  # structs.FragmentState
  # Configure the fragment shader.
  fragment_config = {
    "module": frag_shader,
    "entry_point": "main",
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

def main() -> None:
  # Provision the UI.
  app = wx.App()
  app_window = AppWindow()
  scene_file_path = select_scene()
  scene_data: Obj = parse_scene_file(scene_file_path)
  adapter: wgpu.GPUAdapter = provision_adapter(app_window.canvas)
  device: wgpu.GPUDevice = provision_gpu_device(adapter)
  canvas_context: wgpu.GPUCanvasContext = app_window.canvas.get_context()
  render_pipeline = build_render_pipeline(canvas_context, device)

  print(scene_data)

  # app.MainLoop()

if __name__ == '__main__':
  main()