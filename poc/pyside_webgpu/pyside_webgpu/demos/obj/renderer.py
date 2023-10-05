"""
A module that provides a rendering pipeline for rendering a 3D mesh.
"""
from array import array as create_array

from dataclasses import dataclass, field
import os
from pathlib import Path

import wgpu
import wgpu.backends.rs

from pyside_webgpu.demos.obj.utilities import assemble_camera_data, load_shader
from agents_playground.cameras.camera import Camera3d

from agents_playground.loaders.obj_loader import TriangleMesh
from agents_playground.spatial.matrix import MatrixOrder
from agents_playground.spatial.matrix4x4 import Matrix4x4

@dataclass
class PerFrameData:
  camera_buffer: wgpu.GPUBuffer = field(init=False)

class SimpleRenderer:
  def __init__(self) -> None:
    pass

  def prepare(self, device: wgpu.GPUDevice, mesh: TriangleMesh, camera: Camera3d) -> PerFrameData:
    frame_data = PerFrameData()

    # Load the shaders
    white_model_shader_path = os.path.join(Path.cwd(), 'poc/pyside_webgpu/pyside_webgpu/demos/obj/shaders/white_model.wgsl')
    white_model_shader: wgpu.GPUShaderModule = load_shader(white_model_shader_path, 'White Model Shader', device)

    # structs.PrimitiveState
    # Specify what type of geometry should the GPU render.
    primitive_config={
      "topology":   wgpu.PrimitiveTopology.triangle_list, # type: ignore
      "front_face": wgpu.FrontFace.ccw, # type: ignore Note that the OBJ spec lists verts in ccw order.
      "cull_mode":  wgpu.CullMode.back, # type: ignore
    }

    # structs.VertexState
    # Configure the vertex shader.
    vertex_config = {
      "module": white_model_shader,
      "entry_point": "vs_main",
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
      "module": white_model_shader,
      "entry_point": "fs_main",
      "targets": [
        {
          "format": render_texture_format
        }
      ]
    }

    # Load the 3D mesh into a GPUVertexBuffer.
    # Note: Only items that implement the Python Buffer Protocol are supported for
    # loading into GPUBuffer. 
    vbo_data = create_array('f', mesh.vertices)
    vbo: wgpu.GPUBuffer = device.create_buffer_with_data(
      label = 'Vertex Buffer', 
      data  = vbo_data, 
      usage = wgpu.BufferUsage.VERTEX # type: ignore
    )

    vertex_normals_data = create_array('f', mesh.vertex_normals)
    vertex_normals_buffer: wgpu.GPUBuffer = device.create_buffer_with_data(
      label = 'Vertex Normals Buffer',
      data  = vertex_normals_data,
      usage = wgpu.BufferUsage.VERTEX # type: ignore
    )

    ibo_data = create_array('I', mesh.triangle_index)
    ibo: wgpu.GPUBuffer = device.create_buffer_with_data(
      label = 'Index Buffer',
      data  = ibo_data,
      usage = wgpu.BufferUsage.INDEX # type: ignore
    )

    # Create the Uniform Buffers. This is the data that needs to be passed
    # directly to the shaders. In this use case it's the camera position
    # and the model's affine transformation matrix. 
    # Not getting crazy with this yet. Just get the data to the shader.
    camera_data = assemble_camera_data(camera)
    camera_buffer_size = (4 * 16) + (4 * 16) 
    frame_data.camera_buffer = device.create_buffer(
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
            'buffer': frame_data.camera_buffer,
            'offset': 0,
            'size': frame_data.camera_buffer.size # array_byte_size(camera_data)
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
    queue.write_buffer(frame_data.camera_buffer, 0, camera_data)
    queue.write_buffer(model_world_transform_buffer, 0, model_world_transform_data)

    return frame_data


  def render(self, frame_data:PerFrameData) -> None:
    pass
