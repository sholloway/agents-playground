from array import array as create_array
from array import ArrayType
import os
from pathlib import Path
from typing import Tuple

import wgpu
import wgpu.backends.wgpu_native
from agents_playground.cameras.camera import Camera, Camera3d

from agents_playground.gpu.camera_configuration.camera_configuration_builder import CameraConfigurationBuilder
from agents_playground.gpu.mesh_configuration.builders.mesh_configuration_builder import MeshConfigurationBuilder
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.renderer_builder import RendererBuilder
from agents_playground.gpu.shader_configuration.shader_configuration_builder import ShaderConfigurationBuilder
from agents_playground.gpu.shaders import load_shader

from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.mesh import MeshBuffer

def assemble_camera_data(camera: Camera) -> ArrayType:
  view_matrix = camera.view_matrix
  proj_matrix = camera.projection_matrix
  proj_view: Tuple = \
    proj_matrix.transpose().flatten(MatrixOrder.Row) + \
    view_matrix.flatten(MatrixOrder.Row)
  return create_array('f', proj_view)

class SimpleRendererBuilder(RendererBuilder):
  def __init__(self) -> None:
    super().__init__()
    self._camera_config = CameraConfigurationBuilder()
    self._shader_config = ShaderConfigurationBuilder()
    self._mesh_config = MeshConfigurationBuilder()

  def _load_shaders(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration
  ) -> None:
    white_model_shader_path = os.path.join(Path.cwd(), 'poc/pyside_webgpu/pyside_webgpu/demos/obj/shaders/triangle.wgsl')
    pc.shader = load_shader(white_model_shader_path, 'Triangle Shader', device)

  def _build_pipeline_configuration(
    self, 
    render_texture_format: str,
    pc: PipelineConfiguration,
  ) -> None:
    pc.primitive_config = self._mesh_config.configure_pipeline_primitives()
    pc.vertex_config = self._shader_config.configure_vertex_shader(pc.shader) 
    pc.fragment_config = self._shader_config.configure_fragment_shader(render_texture_format, pc.shader)

  def _load_mesh(
    self, 
    device: wgpu.GPUDevice, 
    mesh: MeshBuffer, 
    frame_data: PerFrameData
  ) -> None:
    # Load the 3D mesh into a GPUVertexBuffer.
    frame_data.vbo = self._mesh_config.create_vertex_buffer(device, mesh.data)
    frame_data.ibo = self._mesh_config.create_index_buffer(device, mesh.index)
    frame_data.num_primitives = len(mesh.index)
    
    
  def _setup_camera(
    self, 
    device: wgpu.GPUDevice, 
    camera: Camera3d, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    pc.camera_data = assemble_camera_data(camera)
    frame_data.camera_buffer = self._camera_config.create_camera_buffer(device, camera)

  def _setup_model_transform(
    self,
    device: wgpu.GPUDevice, 
    model_world_transform: Matrix, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    pc.model_world_transform_data = create_array('f', model_world_transform.flatten(MatrixOrder.Row))
    frame_data.model_world_transform_buffer = self._camera_config.create_model_world_transform_buffer(device)

  def _setup_uniform_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    # Set up the bind group layout for the uniforms.
    pc.camera_uniform_bind_group_layout = self._camera_config.create_camera_ubg_layout(device)
    pc.model_uniform_bind_group_layout = self._camera_config.create_model_ubg_layout(device)

    frame_data.display_config_buffer = device.create_buffer(
      label = 'Display Configuration Buffer',
      size = 4,
      usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST # type: ignore
    )
  
    pc.display_config_bind_group_layout= device.create_bind_group_layout(
      label = 'Display Configuration Uniform Bind Group Layout',
      entries = [
        {
          'binding': 0, # Bind group for the display configuration options.
          'visibility': wgpu.flags.ShaderStage.VERTEX | wgpu.flags.ShaderStage.FRAGMENT, # type: ignore
          'buffer': {
            'type': wgpu.BufferBindingType.uniform # type: ignore
          }
        }
      ]
    )

  def _setup_renderer_pipeline(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(
      label = 'Render Pipeline Layout', 
      bind_group_layouts=[
        pc.camera_uniform_bind_group_layout, 
        pc.model_uniform_bind_group_layout,
        pc.display_config_bind_group_layout
      ]
    )

    depth_stencil_config = {
      'format': wgpu.enums.TextureFormat.depth24plus_stencil8, # type: ignore
      'depth_write_enabled': True,
      'depth_compare': wgpu.enums.CompareFunction.less, # type: ignore
    }

    frame_data.render_pipeline = device.create_render_pipeline(
      label         = 'Simple Rendering Pipeline', 
      layout        = pipeline_layout,
      primitive     = pc.primitive_config,
      vertex        = pc.vertex_config,
      fragment      = pc.fragment_config,
      depth_stencil = depth_stencil_config,
      multisample   = None
    )

  def _create_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    frame_data.camera_bind_group = self._camera_config.create_camera_bind_group(
      device,
      pc.camera_uniform_bind_group_layout,
      frame_data.camera_buffer
    )
    
    frame_data.model_transform_bind_group = self._camera_config.create_model_transform_bind_group(
      device, 
      pc.model_uniform_bind_group_layout, 
      frame_data.model_world_transform_buffer
    )

    frame_data.display_config_bind_group = device.create_bind_group(
      label   = 'Display Configuration Bind Group',
      layout  = pc.display_config_bind_group_layout,
      entries = [
        {
          'binding': 0,
          'resource': {
            'buffer':  frame_data.display_config_buffer,
            'offset': 0,
            'size': frame_data.display_config_buffer.size #array_byte_size(model_world_transform_data)
          }
        }
      ]
    )

  def _load_uniform_buffers(
    self,
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    queue: wgpu.GPUQueue = device.queue
    queue.write_buffer(frame_data.camera_buffer, 0, pc.camera_data)
    queue.write_buffer(frame_data.model_world_transform_buffer, 0, pc.model_world_transform_data)
    queue.write_buffer(frame_data.display_config_buffer, 0, create_array('i', [0]))
