from array import array as create_array
import os
from pathlib import Path

import wgpu
import wgpu.backends.wgpu_native
from agents_playground.cameras.camera import Camera3d

from agents_playground.gpu.camera_configuration.camera_configuration_builder import CameraConfigurationBuilder
from agents_playground.gpu.mesh_configuration.builders.normals_mesh_configuration_builder import NormalsMeshConfigurationBuilder
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.renderer_builder import RendererBuilder, assemble_camera_data
from agents_playground.gpu.renderers.gpu_renderer import GPURendererException
from agents_playground.gpu.shader_configuration.normals_shader_configuration_builder import NormalsShaderConfigurationBuilder
from agents_playground.gpu.shaders import load_shader
from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.mesh import MeshBuffer

class NormalsRendererBuilder(RendererBuilder):
  def __init__(self) -> None:
    super().__init__()
    self._camera_config = CameraConfigurationBuilder()
    self._shader_config = NormalsShaderConfigurationBuilder()
    self._mesh_config = NormalsMeshConfigurationBuilder()

  def _load_shaders(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration
  ) -> None:
    shader_path: str = os.path.join(Path.cwd(), 'agents_playground/gpu/shaders/normals.wgsl')
    pc.shader = load_shader(shader_path, 'Normals Shader', device)

  def _build_pipeline_configuration(
    self, 
    render_texture_format: str,
    pc: PipelineConfiguration,
  ) -> None:
    pc.primitive_config = self._mesh_config.configure_pipeline_primitives()
    pc.vertex_config    = self._shader_config.configure_vertex_shader(pc.shader) 
    pc.fragment_config  = self._shader_config.configure_fragment_shader(render_texture_format, pc.shader)

  def _load_mesh(
    self, 
    device: wgpu.GPUDevice, 
    mesh: MeshBuffer, 
    frame_data: PerFrameData
  ) -> None:
    # Load the 3D mesh into a GPUVertexBuffer.
    frame_data.normals_vbo = self._mesh_config.create_vertex_buffer(device, mesh.data)
    frame_data.normals_ibo = self._mesh_config.create_index_buffer(device, mesh.index)
    frame_data.normals_num_primitives = mesh.count


  def _setup_camera(
    self, 
    device: wgpu.GPUDevice, 
    camera: Camera3d, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    pc.camera_data = assemble_camera_data(camera)
    if frame_data.camera_buffer is None:
      # The camera may have already been setup. Only create a buffer if this is 
      # the first render to be constructed.
      frame_data.camera_buffer = self._camera_config.create_camera_buffer(device, camera)
  
  def _setup_model_transform(
    self,
    device: wgpu.GPUDevice, 
    model_world_transform: Matrix, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    pc.model_world_transform_data = create_array('f', model_world_transform.flatten(MatrixOrder.Row))
    if frame_data.model_world_transform_buffer is None:
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

  def _setup_renderer_pipeline(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(
      label = 'Normals Render Pipeline Layout', 
      bind_group_layouts=[
        pc.camera_uniform_bind_group_layout, 
        pc.model_uniform_bind_group_layout,
      ]
    )

    depth_stencil_config = {
      'format': wgpu.enums.TextureFormat.depth24plus_stencil8, # type: ignore
      'depth_write_enabled': True,
      'depth_compare': wgpu.enums.CompareFunction.less, # type: ignore
    }

    frame_data.normals_render_pipeline = device.create_render_pipeline(
      label         = 'Normals Rendering Pipeline', 
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
    if frame_data.camera_buffer is None or  frame_data.model_world_transform_buffer is None:
      raise GPURendererException('Attempted to bind groups but one or more of the buffers is not set.')

    frame_data.normals_camera_bind_group = self._camera_config.create_camera_bind_group(
      device,
      pc.camera_uniform_bind_group_layout,
      frame_data.camera_buffer  
    )
    
    frame_data.normals_model_transform_bind_group = self._camera_config.create_model_transform_bind_group(
      device, 
      pc.model_uniform_bind_group_layout, 
      frame_data.model_world_transform_buffer
    )

  def _load_uniform_buffers(
    self,
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    pass 
    # queue: wgpu.GPUQueue = device.queue
    # if frame_data.camera_buffer is None:
    #   queue.write_buffer(frame_data.camera_buffer, 0, pc.camera_data)

    # if frame_data.model_world_transform_buffer is None:
    #   queue.write_buffer(frame_data.model_world_transform_buffer, 0, pc.model_world_transform_data)