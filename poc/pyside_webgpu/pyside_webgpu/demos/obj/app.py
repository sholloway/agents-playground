"""
This module is a simple implementation of a model viewer that 
can load Obj models.

To Run
poetry run python -X dev poc/pyside_webgpu/pyside_webgpu/demos/obj/app.py
"""
import array

from agents_playground.cameras.camera import Camera3d
from agents_playground.spatial.matrix import MatrixOrder
from agents_playground.spatial.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector3d import Vector3d
create_array = array.array

from functools import partial
import os
from pathlib import Path
from typing import List, Tuple

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

def load_shader(shader_path: str, name: str, device: wgpu.GPUDevice) -> wgpu.GPUShaderModule:
  with open(file = shader_path, mode = 'r') as filereader:
    shader_code = filereader.read()
  return device.create_shader_module(
    label = name,
    code  = shader_code
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
    "clear_value": (1, 0, 0, 1),   # Clear to Red.
    "load_op": wgpu.LoadOp.clear,  # type: ignore
    "store_op": wgpu.StoreOp.store # type: ignore
  }

  command_encoder = device.create_command_encoder()

  # The first command to encode is the instruction to do a 
  # rendering pass.
  pass_encoder: wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
    color_attachments=[color_attachment]
  )

  pass_encoder.set_pipeline(render_pipeline)
  # pass_encoder.set_viewport(0, 0, canvas_context)
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

def assemble_camera_data(camera: Camera3d) -> array.ArrayType:
  view_matrix = camera.to_view_matrix()
  proj_matrix = camera.projection_matrix
  proj_view: Tuple = \
    proj_matrix.flatten(MatrixOrder.Row) + \
    view_matrix.transpose().flatten(MatrixOrder.Row)
  return create_array('f', proj_view)

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

  # Load the shaders
  vert_shader_path = os.path.join(Path.cwd(), 'poc/pyside_webgpu/pyside_webgpu/demos/obj/shaders/white_model.vert.wgsl')
  frag_shader_path = os.path.join(Path.cwd(), 'poc/pyside_webgpu/pyside_webgpu/demos/obj/shaders/white_model.frag.wgsl')
  vert_shader: wgpu.GPUShaderModule = load_shader(vert_shader_path, 'White Model Vertex Shader', device)
  frag_shader: wgpu.GPUShaderModule = load_shader(frag_shader_path, 'White Model Fragment Shader', device)

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
  
  # Load the 3D mesh into memory
  model_file_path = select_model()
  model_data: Obj = parse_model_file(model_file_path)

  # Load the 3D mesh into a GPUVertexBuffer.
  # Note: Only items that implement the Python Buffer Protocol are supported for
  # loading into GPUBuffer. 
  tri_mesh = TriangleMesh.from_obj(model_data)
  vbo_data = create_array('f', tri_mesh.vertices)
  vbo: wgpu.GPUBuffer = device.create_buffer_with_data(
    label = 'Vertex Buffer', 
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
    label = 'Index Buffer',
    data  = ibo_data,
    usage = wgpu.BufferUsage.INDEX # type: ignore
  )
  
  # Create the Uniform Buffers. This is the data that needs to be passed
  # directly to the shaders. In this use case it's the camera position
  # and the model's affine transformation matrix. 
  # Not getting crazy with this yet. Just get the data to the shader.
  
  camera = Camera3d(
    projection_matrix = Matrix4x4.identity(),
    right    = Vector3d(1, 0, 0),
    up       = Vector3d(0, 1, 0),
    facing   = Vector3d(0, 0, 1),
    position = Vector3d(0, 0, 0),
  )

  camera_data = assemble_camera_data(camera)

  camera_buffer_size = (4 * 16) + (4 * 16) 
  camera_buffer: wgpu.GPUBuffer = device.create_buffer(
    label = 'Camera Buffer',
    size = camera_buffer_size,
    usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST # type: ignore
  )
  
  # The transformation to apply to the 3D model.
  # Right now just get the data pipeline wired up.
  # This will probably need to change to locate the model at the origin and 
  # to scale it up.
  model_world_transform = Matrix4x4.identity()
  model_world_transform_data = create_array('f', model_world_transform.flatten(MatrixOrder.Row))
  
  model_world_transform_buffer: wgpu.GPUBuffer = device.create_buffer(
    label = 'Model Transform Buffer',
    size = 4 * 16,
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

  bound_update_camera = partial(update_camera, camera)
  bound_update_uniforms = partial(update_uniforms, device, camera_buffer, camera)

  app_window.set_ui_update_handler(bound_update_camera)
  app_window.set_update_uniforms_handler(bound_update_uniforms)

  # Build the Rending Pipeline
  pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(
    label = 'Render Pipeline Layout', 
    bind_group_layouts=[
      camera_uniform_bind_group_layout, 
      model_uniform_bind_group_layout
    ]
  )

  render_pipeline: wgpu.GPURenderPipeline = device.create_render_pipeline(
    label         = 'Rendering Pipeline', 
    layout        = pipeline_layout,
    primitive     = primitive_config,
    vertex        = vertex_config,
    fragment      = fragment_config,
    depth_stencil = None,
    multisample   = None
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
          'size': camera_buffer.size # array_byte_size(camera_data)
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
          'size': model_world_transform_buffer.size #array_byte_size(model_world_transform_data)
        }
      }
    ]
  )

  # Load the uniform buffers.
  queue: wgpu.GPUQueue = device.queue
  queue.write_buffer(camera_buffer, 0, camera_data)
  queue.write_buffer(model_world_transform_buffer, 0, model_world_transform_data)


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

"""
Next Steps:
- Create a GUI control that allows dynamically setting the Shader Uniforms.
- Get the camera sorted out before trying to troubleshoot the meshes. 
  TODO: Need to update the uniforms and request a redraw after the UI is updated.
"""