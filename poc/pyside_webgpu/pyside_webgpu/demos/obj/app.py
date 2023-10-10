"""
This module is a simple implementation of a model viewer that 
can load Obj models.

To Run
poetry run python -X dev poc/pyside_webgpu/pyside_webgpu/demos/obj/app.py
"""
from array import array as create_array

from functools import partial
import os
from pathlib import Path
from typing import List, Tuple
from pyside_webgpu.demos.obj.renderers.edge.edge_renderer import EdgeRenderer
from pyside_webgpu.demos.obj.renderers.frame_data import PerFrameData
from pyside_webgpu.demos.obj.renderers.renderer import GPURenderer
from pyside_webgpu.demos.obj.renderers.simple.simple_renderer import SimpleRenderer
from pyside_webgpu.demos.obj.utilities import assemble_camera_data

import wx
import wgpu
import wgpu.backends.rs

from agents_playground.cameras.camera import Camera3d
from agents_playground.loaders.obj_loader import EdgeMesh, ObjLoader, Obj, TriangleMesh
from agents_playground.spatial.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector3d import Vector3d

from pyside_webgpu.demos.obj.ui import AppWindow

# Setup granular logging and tracing.
import logging
# logger = logging.getLogger("wgpu")
wgpu.logger.setLevel("DEBUG")
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler()
rootLogger.addHandler(consoleHandler)
ENABLE_WGPU_TRACING = True 

def select_model() -> str:
  """
  Find the path for the desired scene.
  """
  scene_dir = 'poc/pyside_webgpu/pyside_webgpu/demos/obj/models'
  scene_filename = 'cube.obj'
  return os.path.join(Path.cwd(), scene_dir, scene_filename)

def parse_model_file(scene_file_path: str) -> Obj:
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

def draw_frame(
  canvas_context: wgpu.GPUCanvasContext, 
  device: wgpu.GPUDevice,
  renderer: GPURenderer,
  frame_data: PerFrameData
):
  current_texture_view: wgpu.GPUCanvasContext = canvas_context.get_current_texture()

  # struct.RenderPassColorAttachment
  color_attachment = {
    "view": current_texture_view,
    "resolve_target": None,
    "clear_value": (0.5, 0.5, 0.5, 1),   # Clear to Gray.
    "load_op": wgpu.LoadOp.clear,  # type: ignore
    "store_op": wgpu.StoreOp.store # type: ignore
  }

  command_encoder = device.create_command_encoder()

  # The first command to encode is the instruction to do a 
  # rendering pass.
  pass_encoder: wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
    color_attachments=[color_attachment]
  )

  pass_encoder.set_pipeline(frame_data.render_pipeline)
  renderer.render(pass_encoder, frame_data)

  pass_encoder.end()
  device.queue.submit([command_encoder.finish()])

def update_camera(
  camera: Camera3d, 
  x:float | None = None, 
  y: float | None = None,
  z: float | None = None,
  right_i: float | None = None,
  right_j: float | None = None,
  right_k: float | None = None,
  up_i: float | None = None,
  up_j: float | None = None,
  up_k: float | None = None,
  facing_i: float | None = None,
  facing_j: float | None = None,
  facing_k: float | None = None
) -> None:
  x = x if x is not None else camera.position.i
  y = y if y is not None else camera.position.j
  z = z if z is not None else camera.position.k

  right_i = right_i if right_i is not None else camera.right.i
  right_j = right_j if right_j is not None else camera.right.j
  right_k = right_k if right_k is not None else camera.right.k

  up_i = up_i if up_i is not None else camera.up.i
  up_j = up_j if up_j is not None else camera.up.j
  up_k = up_k if up_k is not None else camera.up.k
  
  facing_i = facing_i if facing_i is not None else camera.facing.i
  facing_j = facing_j if facing_j is not None else camera.facing.j
  facing_k = facing_k if facing_k is not None else camera.facing.k

  camera.position = Vector3d(x,y, z)
  camera.right = Vector3d(right_i, right_j, right_k)
  camera.up = Vector3d(up_i, up_j, up_k)
  camera.facing = Vector3d(facing_i, facing_j, facing_k)

def update_uniforms(
  device: wgpu.GPUDevice, 
  camera_buffer: wgpu.GPUBuffer, 
  camera: Camera3d) -> None:
  camera_data = assemble_camera_data(camera)
  device.queue.write_buffer(camera_buffer, 0, camera_data)

def main() -> None:
  # Provision the UI.
  app = wx.App()
  app_window = AppWindow()

  # Initialize WebGPU
  adapter: wgpu.GPUAdapter = provision_adapter(app_window.canvas)
  device: wgpu.GPUDevice = provision_gpu_device(adapter)
  if ENABLE_WGPU_TRACING:
    device.adapter.request_device_tracing('./wgpu_traces') # type: ignore
  canvas_context: wgpu.GPUCanvasContext = app_window.canvas.get_context()

  # Set the GPUCanvasConfiguration to control how drawing is done.
  render_texture_format = canvas_context.get_preferred_format(device.adapter)
  canvas_context.configure(
    device       = device, 
    usage        = wgpu.flags.TextureUsage.RENDER_ATTACHMENT, # type: ignore
    format       = render_texture_format,
    view_formats = [],
    color_space  = 'srgb',
    alpha_mode   = 'opaque'
  )
  
  # Load the 3D mesh into memory
  model_file_path = select_model()
  model_data: Obj = parse_model_file(model_file_path)

  # mesh = TriangleMesh.from_obj(model_data)
  mesh = EdgeMesh.from_obj(model_data)
  assert len(mesh.index) == 36, "There should be 36 (12 * 3) edges."
  
  # Note: The way I'm calculating the aspect ratio could be completely wrong.
  # Based on: https://docs.wxpython.org/wx.glcanvas.GLCanvas.html
  canvas_size = app_window.canvas.get_physical_size()
  aspect_ratio = canvas_size[0]/canvas_size[1]

  camera = Camera3d.look_at(
    position = Vector3d(10, 10, 10),
    up       = Vector3d(0, 1, 0),
    target   = Vector3d(0, 0, 0),
    projection_matrix = Matrix4x4.perspective(aspect_ratio),
  )

  # The transformation to apply to the 3D model.
  # Note: This should be passed in...
  # Right now just get the data pipeline wired up.
  # This will probably need to change to locate the model at the origin and 
  # to scale it up.
  model_world_transform = Matrix4x4.identity()

  # renderer: GPURenderer = SimpleRenderer()
  renderer: GPURenderer = EdgeRenderer()

  frame_data: PerFrameData = renderer.prepare(
    device, 
    render_texture_format, 
    mesh,
    camera,
    model_world_transform
  )

  bound_update_camera = partial(update_camera, camera)
  bound_update_uniforms = partial(update_uniforms, device, frame_data.camera_buffer, camera)
  bound_draw_frame = partial(draw_frame, canvas_context, device, renderer, frame_data)

  app_window.set_ui_update_handler(bound_update_camera)
  app_window.set_update_uniforms_handler(bound_update_uniforms)
  app_window.canvas.request_draw(bound_draw_frame)

  # Launch the GUI.
  app.MainLoop()

if __name__ == '__main__':
  main()