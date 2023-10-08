from array import array as create_array
import os
from pathlib import Path

from pyside_webgpu.demos.obj.renderers.simple.camera_configuration_builder import CameraConfigurationBuilder
from agents_playground.cameras.camera import Camera3d
from agents_playground.loaders.obj_loader import Mesh

from pyside_webgpu.demos.obj.renderers.edge.mesh_configuration_builder import MeshConfigurationBuilder
from pyside_webgpu.demos.obj.renderers.edge.shader_configuration_builder import ShaderConfigurationBuilder
from pyside_webgpu.demos.obj.renderers.frame_data import PerFrameData
from pyside_webgpu.demos.obj.renderers.pipeline_configuration import PipelineConfiguration
from pyside_webgpu.demos.obj.renderers.renderer_builder import RendererBuilder
from pyside_webgpu.demos.obj.utilities import assemble_camera_data, load_shader

import wgpu
import wgpu.backends.rs

from agents_playground.spatial.matrix import Matrix, MatrixOrder

class EdgeRendererConfigurationBuilder(RendererBuilder):
  def __init__(self) -> None:
    super().__init__()
    self._mesh_config = MeshConfigurationBuilder()
    self._shader_config = ShaderConfigurationBuilder()
    self._camera_config = CameraConfigurationBuilder() # TODO: Right now this is using the same config as the simple renderer.

  def _load_shaders(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration
  ) -> None:
    shader_path = os.path.join(Path.cwd(), 'poc/pyside_webgpu/pyside_webgpu/demos/obj/shaders/edge.wgsl')
    pc.shader = load_shader(shader_path, 'Triangle Edge Shader', device)

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
    mesh: Mesh, 
    frame_data: PerFrameData
  ) -> None:
    frame_data.vbo = self._mesh_config.create_vertex_buffer(device, mesh.vertices)

    # I don't kneed the vert normals to draw the edges, but including them to enable doing stuff with them later.
    frame_data.vertex_normals_buffer = self._mesh_config.create_vertex_normals_buffer(device, mesh.vertex_normals)

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
    pc: PipelineConfiguration
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
      label = 'Render Pipeline Layout', 
      bind_group_layouts=[
        pc.camera_uniform_bind_group_layout, 
        pc.model_uniform_bind_group_layout
      ]
    )

    frame_data.render_pipeline = device.create_render_pipeline(
      label         = 'Rendering Pipeline', 
      layout        = pipeline_layout,
      primitive     = pc.primitive_config,
      vertex        = pc.vertex_config,
      fragment      = pc.fragment_config,
      depth_stencil = None,
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
  
  def _load_uniform_buffers(
    self,
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    queue: wgpu.GPUQueue = device.queue
    queue.write_buffer(frame_data.camera_buffer, 0, pc.camera_data)
    queue.write_buffer(frame_data.model_world_transform_buffer, 0, pc.model_world_transform_data)