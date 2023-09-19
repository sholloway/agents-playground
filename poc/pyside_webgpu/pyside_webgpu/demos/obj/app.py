"""
This module is a simple implementation of a model viewer that 
can load Obj models.

To Run
poetry run python -X dev pyside_webgpu/demos/obj/app.py
"""
from functools import partial
from array import array
import os
from pathlib import Path
from typing import List

import wx
import wgpu
import wgpu.backends.rs

from agents_playground.loaders.obj_loader import ObjLoader, Obj, TriangleMesh
from pyside_webgpu.demos.obj.ui import AppWindow

def select_model() -> str:
  """
  Find the path for the desired scene.
  """
  scene_dir = 'pyside_webgpu/demos/obj/models'
  scene_filename = 'skull.obj'
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

  # Not currently using any uniforms that need bind groups so creating an 
  # empty pipeline layout.
  pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(
    label = 'Render Pipeline Layout', 
    bind_group_layouts=[]
  )

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
    "constants": {},
    "buffers": [ # structs.VertexBufferLayout
      {
        'array_stride': 4 * 3,                   # sizeof(float) * 3
        'step_mode': wgpu.VertexStepMode.vertex, # type: ignore
        'attributes': [                          # structs.VertexAttribute
          {
            'format': wgpu.VertexFormat.float32x3, # type: ignore
            'offset': 0,
            'shader_location': 0
          }
        ]
      }
    ],
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

def draw_frame(
  canvas_context: wgpu.GPUCanvasContext, 
  device: wgpu.GPUDevice,
  render_pipeline: wgpu.GPURenderPipeline,
  vbo: wgpu.GPUBuffer, 
  ibo: wgpu.GPUBuffer,
  num_triangles: int
):
  current_texture_view: wgpu.GPUCanvasContext = canvas_context.get_current_texture()

  # struct.RenderPassColorAttachment
  color_attachment = {
    "view": current_texture_view,
    "resolve_target": None,
    "clear_value": (0, 0, 0, 1),
    "load_op": wgpu.LoadOp.clear,  # type: ignore
    "store_op": wgpu.StoreOp.store # type: ignore
  }

  command_encoder = device.create_command_encoder()

  # The first command to encode is the instruction to do a 
  # rendering pass.
  pass_encoder: wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
    color_attachments=[color_attachment],
  )

  print('The Render Pipeline')
  print(render_pipeline._internal)
  pass_encoder.set_pipeline(render_pipeline)
  # pass_encoder.set_viewport(0, 0, canvas_context.)
  # pass_encoder.set_scissor_rect()
  pass_encoder.set_vertex_buffer(slot = 0, buffer = vbo)
  pass_encoder.set_index_buffer(buffer = ibo, index_format=wgpu.IndexFormat.uint32) # type: ignore
  pass_encoder.draw_indexed(
    index_count    = num_triangles, 
    instance_count = 1, 
    first_index    = 0, 
    base_vertex    = 0, 
    first_instance = 0
  )  
  pass_encoder.end()

  device.queue.submit([command_encoder.finish()])


def main() -> None:
  # Provision the UI.
  app = wx.App()
  app_window = AppWindow()
  
  # Load the 3D mesh into memory
  model_file_path = select_model()
  model_data: Obj = parse_model_file(model_file_path)
  print(model_data)

  # Setup WebGPU
  adapter: wgpu.GPUAdapter = provision_adapter(app_window.canvas)
  device: wgpu.GPUDevice = provision_gpu_device(adapter)
  canvas_context: wgpu.GPUCanvasContext = app_window.canvas.get_context()

  # Load the 3D mesh into a GPUVertexBuffer.
  # Note: Only items that implement the Python Buffer Protocol are supported for
  # loading into GPUBuffer. 
  tri_mesh = TriangleMesh.from_obj(model_data)
  vbo_data = array('f', tri_mesh.triangle_data)
  vbo: wgpu.GPUBuffer = device.create_buffer_with_data(
    label = 'vertex_buffer_object', 
    data  = vbo_data, 
    usage = wgpu.BufferUsage.VERTEX # type: ignore
  )

  ibo_data = array('I', tri_mesh.triangle_index)
  ibo: wgpu.GPUBuffer = device.create_buffer_with_data(
    label = 'index_buffer_object',
    data  = ibo_data,
    usage = wgpu.BufferUsage.INDEX # type: ignore
  )

  # Create the Uniform Buffers. This is the data that needs to be passed
  # Directly to the shaders. In this use case it's the camera position
  # and the model's affine transformation matrix. 


  
  # Setup the graphics pipeline
  render_pipeline = build_render_pipeline(canvas_context, device)

  # Setup the draw call.
  bound_draw_frame = partial(
    draw_frame, 
    canvas_context, 
    device, 
    render_pipeline, 
    vbo, 
    ibo, 
    len(tri_mesh.triangle_index)
  )
  app_window.canvas.request_draw(bound_draw_frame)

  # Launch the GUI.
  app.MainLoop()

if __name__ == '__main__':
  main()

"""
TODO
- [X] Bug: Why is the Obj file empty?
- [X] Todo: Load the Obj data into a GPUVertextBuffer.
- [X] TODO: Rewrite the draw_frame function to work with this app.
- [ ] TODO: Handle loading the 
- [ ] TODO: Handle the camera
- [ ] TODO: Handle the model's affine transformation matrix.
"""