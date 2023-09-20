"""
This module is a simple implementation of a model viewer that 
can load Obj models.

To Run
poetry run python -X dev poc/pyside_webgpu/pyside_webgpu/demos/obj/app.py
"""
import array
create_array = array.array

from functools import partial
import os
from pathlib import Path
from typing import List

import wx
import wgpu
import wgpu.backends.rs

# Setup granular logging and tracing.
import logging
# logger = logging.getLogger("wgpu")
wgpu.logger.setLevel("DEBUG")
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler()
rootLogger.addHandler(consoleHandler)
ENABLE_WGPU_TRACING = True 

from agents_playground.loaders.obj_loader import ObjLoader, Obj, TriangleMesh
from pyside_webgpu.demos.obj.ui import AppWindow

def array_byte_size(a: array.array) -> int:
  """Finds the size, in bytes, of a given array."""
  return a.buffer_info()[1]*a.itemsize

def select_model() -> str:
  """
  Find the path for the desired scene.
  """
  scene_dir = 'poc/pyside_webgpu/pyside_webgpu/demos/obj/models'
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
  device: wgpu.GPUDevice,
  camera_uniform_bind_group_layout: wgpu.GPUBindGroupLayout,
  model_uniform_bind_group_layout: wgpu.GPUBindGroupLayout
) -> wgpu.GPURenderPipeline:
  """
  Create the WebGPU Render Pipeline.
  """
  # Load the shaders
  vert_shader_path = os.path.join(Path.cwd(), 'poc/pyside_webgpu/pyside_webgpu/demos/obj/shaders/white_model.vert.wgsl')
  frag_shader_path = os.path.join(Path.cwd(), 'poc/pyside_webgpu/pyside_webgpu/demos/obj/shaders/white_model.frag.wgsl')
  vert_shader: wgpu.GPUShaderModule = load_shader(vert_shader_path, 'vert_shader', device)
  frag_shader: wgpu.GPUShaderModule = load_shader(frag_shader_path, 'frag_shader', device)

  pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(
    label = 'Render Pipeline Layout', 
    bind_group_layouts=[
      camera_uniform_bind_group_layout, 
      model_uniform_bind_group_layout
    ]
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
    "topology":   wgpu.PrimitiveTopology.triangle_list, # type: ignore
    "front_face": wgpu.FrontFace.ccw, # type: ignore
    "cull_mode":  wgpu.CullMode.none, # type: ignore
  }


  # structs.VertexState
  # Configure the vertex shader.
  vertex_config = {
    "module": vert_shader,
    "entry_point": "main",
    "constants": {},
    "buffers": [ # structs.VertexBufferLayout
      {
        'array_stride': 4 * 4,                   # sizeof(float) * 4
        'step_mode': wgpu.VertexStepMode.vertex, # type: ignore
        'attributes': [                          # structs.VertexAttribute
          {
            'shader_location': 0,
            'format': wgpu.VertexFormat.float32x4, # type: ignore This is of the form: x,y,z,w
            'offset': 0
          }
        ]
      },
      {
        'array_stride': 4 * 3,                   # sizeof(float) * 3
        'step_mode': wgpu.VertexStepMode.vertex, # type: ignore
        'attributes': [                          # structs.VertexAttribute
          {
            'format': wgpu.VertexFormat.float32x3, # type: ignore This is of the form: i, j, k
            'offset': 0,
            'shader_location': 1
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
        "format": render_texture_format
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
  vertex_normals_buffer: wgpu.GPUBuffer,
  ibo: wgpu.GPUBuffer,
  num_triangles: int,
  camera_bind_group: wgpu.GPUBindGroup,
  model_transform_bind_group: wgpu.GPUBindGroup
):
  current_texture_view: wgpu.GPUCanvasContext = canvas_context.get_current_texture()

  # struct.RenderPassColorAttachment
  color_attachment = {
    "view": current_texture_view,
    "resolve_target": None,
    "clear_value": (0, 0, 0, 1),   # Clear to Black.
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
  pass_encoder.set_bind_group(0, camera_bind_group, [], 0, 99999)
  pass_encoder.set_bind_group(1, model_transform_bind_group, [], 0, 99999)
  pass_encoder.set_vertex_buffer(slot = 0, buffer = vbo)
  pass_encoder.set_vertex_buffer(slot = 1, buffer = vertex_normals_buffer)
  pass_encoder.set_index_buffer(buffer = ibo, index_format=wgpu.IndexFormat.uint32) # type: ignore

  pass_encoder.draw_indexed(
    index_count    = num_triangles, 
    instance_count = 1, 
    first_index    = 0, 
    base_vertex    = 0, 
    first_instance = 0
  )  
  
  # Can I inspect the pass_encoder to figure out the VBO layout issue?
  print(dir(pass_encoder))

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

  if ENABLE_WGPU_TRACING:
    device.adapter.request_device_tracing('./wgpu_traces') # type: ignore

  # Load the 3D mesh into a GPUVertexBuffer.
  # Note: Only items that implement the Python Buffer Protocol are supported for
  # loading into GPUBuffer. 
  tri_mesh = TriangleMesh.from_obj(model_data)
  vbo_data = create_array('f', tri_mesh.vertices)
  vbo: wgpu.GPUBuffer = device.create_buffer_with_data(
    label = 'vertex_buffer_object', 
    data  = vbo_data, 
    usage = wgpu.BufferUsage.VERTEX # type: ignore
  )

  vertex_normals_data = create_array('f', tri_mesh.vertex_normals)
  vertex_normals_buffer: wgpu.GPUBuffer = device.create_buffer_with_data(
    label = 'Vertex Normals Buffer',
    data  = vertex_normals_data,
    usage = wgpu.BufferUsage.VERTEX # type: ignore
  )

  ibo_data = create_array('I', tri_mesh.triangle_index)
  ibo: wgpu.GPUBuffer = device.create_buffer_with_data(
    label = 'index_buffer_object',
    data  = ibo_data,
    usage = wgpu.BufferUsage.INDEX # type: ignore
  )
  
  # Create the Uniform Buffers. This is the data that needs to be passed
  # directly to the shaders. In this use case it's the camera position
  # and the model's affine transformation matrix. 
  # Not getting crazy with this yet. Just get the data to the shader.
  camera = [
    # Projection Matrix (mat4x4<f32>)
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1,

    # View Matrix (mat4x4<f32>)
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1,

    # Camera Position Vector (vec3<f32>)
    1, 0, 0
  ]

  camera_data = create_array('f', camera)
  camera_buffer: wgpu.GPUBuffer = device.create_buffer_with_data(
    label = 'Camera Buffer',
    data = camera_data, 
    usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST # type: ignore
  )
  
  # The transformation to apply to the 3D model.
  # Right now just get the data pipeline wired up.
  # This will probably need to change to locate the model at the origin and 
  # to scale it up.
  model_world_transform = [
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1,
  ]
  model_world_transform_data = create_array('f', model_world_transform)
  model_world_transform_buffer: wgpu.GPUBuffer = device.create_buffer_with_data(
    label = 'Model Transform Buffer',
    data = model_world_transform_data,
    usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST # type: ignore
  )

  # Set up the bind group layout for the uniforms.
  camera_uniform_bind_group_layout: wgpu.GPUBindGroupLayout = device.create_bind_group_layout(
    label = 'Camera Uniform Bind Group Layout',
    entries = [
      {
        'binding': 0, # Bind group for the camera.
        'visibility': wgpu.flags.ShaderStage.VERTEX, # type: ignore
        'buffer': {
          'type': wgpu.BufferBindingType.uniform # type: ignore
        }
      }
    ]
  )
  
  model_uniform_bind_group_layout: wgpu.GPUBindGroupLayout = device.create_bind_group_layout(
    label = 'Model Transform Uniform Bind Group Layout',
    entries = [
      {
        'binding': 0, # Bind group for the camera.
        'visibility': wgpu.flags.ShaderStage.VERTEX, # type: ignore
        'buffer': {
          'type': wgpu.BufferBindingType.uniform # type: ignore
        }
      }
    ]
  )

  camera_bind_group: wgpu.GPUBindGroup =  device.create_bind_group(
    label   = 'Camera Bind Group',
    layout  = camera_uniform_bind_group_layout,
    entries = [
      {
        'binding': 0,
        'resource': {
          'buffer': camera_buffer,
          'offset': 0,
          'size': array_byte_size(camera_data)
        }
      }
    ]
  )
  
  model_transform_bind_group: wgpu.GPUBindGroup =  device.create_bind_group(
    label   = 'Model Transform Bind Group',
    layout  = model_uniform_bind_group_layout,
    entries = [
      {
        'binding': 0,
        'resource': {
          'buffer': model_world_transform_buffer,
          'offset': 0,
          'size': array_byte_size(model_world_transform_data)
        }
      }
    ]
  )

  # Setup the graphics pipeline
  render_pipeline = build_render_pipeline(
    canvas_context, 
    device,
    camera_uniform_bind_group_layout,
    model_uniform_bind_group_layout
  )

  # Setup the draw call.
  bound_draw_frame = partial(
    draw_frame, 
    canvas_context, 
    device, 
    render_pipeline, 
    vbo, 
    vertex_normals_buffer,
    ibo, 
    len(tri_mesh.triangle_index),
    camera_bind_group,
    model_transform_bind_group
  )
  app_window.canvas.request_draw(bound_draw_frame)

  # Launch the GUI.
  app.MainLoop()

if __name__ == '__main__':
  main()