from array import array as create_array
import os
from pathlib import Path
import wgpu
import wgpu.backends.wgpu_native

from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.fp import Something
from agents_playground.gpu.camera_configuration.camera_configuration_builder import CameraConfigurationBuilder
from agents_playground.gpu.mesh_configuration.builders.triangle_list_mesh_configuration_builder import TriangleListMeshConfigurationBuilder
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.renderer_builder import RendererBuilder, assemble_camera_data
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer, GPURendererException
from agents_playground.gpu.shader_configuration.default_shader_configuration_builder import DefaultShaderConfigurationBuilder
from agents_playground.gpu.shaders import load_shader
from agents_playground.scene import Scene
from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.matrix.transformation import TransformationConfiguration
from agents_playground.spatial.mesh import MeshBuffer, MeshData

class AgentRendererBuilder(RendererBuilder):
  def __init__(self) -> None:
    super().__init__()
    self._camera_config = CameraConfigurationBuilder()
    self._shader_config = DefaultShaderConfigurationBuilder()
    self._mesh_config   = TriangleListMeshConfigurationBuilder('Agent')

  def _load_shaders(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration
  ) -> None:
    shader_path: str = os.path.join(Path.cwd(), 'agents_playground/gpu/shaders/agent.wgsl')
    pc.shader = load_shader(shader_path, 'Agent Triangle Shader', device)

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
    mesh_data: MeshData, 
    frame_data: PerFrameData
  ) -> None:
    # Load the 3D mesh into a GPUVertexBuffer.
    vertex_buffer: MeshBuffer = mesh_data.vertex_buffer.unwrap()
    vertex_buffer.vbo         = self._mesh_config.create_vertex_buffer(device, vertex_buffer.data)
    vertex_buffer.ibo         = self._mesh_config.create_index_buffer(device, vertex_buffer.index)
    # frame_data.landscape_num_primitives = vertex_buffer.count

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

  def _setup_model_transforms(
    self,
    device: wgpu.GPUDevice, 
    scene: Scene, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    """
    Loop over the agents and establish their initial transformations.
    """
    for agent in scene.agents:
      if agent.position.transformation.is_something():
        transformation: TransformationConfiguration = agent.position.transformation.unwrap()
        transformation.transform()

        # I think I don't need a dedicated GPUBuffer for each agents. 
        # Just one for the AgentRenderer, then load the array data into it .
        self.agent_transformation_buffer = Something(
          device.create_buffer(
            label = 'Agent Transform Buffer',
            size = 4 * 16, # The size of a 4x4 matrix of floats.
            usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST # type: ignore
          )
        )

  def _setup_uniform_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    scene: Scene,
    pc: PipelineConfiguration,
    frame_data: PerFrameData
  ) -> None:
    # Set up the bind group layout for the uniforms.
    pc.camera_uniform_bind_group_layout = self._camera_config.create_camera_ubg_layout(device)
    pc.model_uniform_bind_group_layout = self._camera_config.create_model_ubg_layout(device)

    if frame_data.display_config_buffer is None:
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
      label = 'Agent Render Pipeline Layout', 
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

    return device.create_render_pipeline(
      label         = 'Agent Rendering Pipeline', 
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
    scene: Scene,
    pc: PipelineConfiguration, 
    frame_data: PerFrameData,
    mesh_data: MeshData
  ) -> None:
    if frame_data.camera_buffer is None \
      or frame_data.display_config_buffer is None:
      error_msg = 'Attempted to bind groups but one or more of the buffers is not set.'
      raise GPURendererException(error_msg)
    
    vertex_buffer: MeshBuffer = mesh_data.vertex_buffer.unwrap()

    vertex_buffer.bind_groups[0] = self._camera_config.create_camera_bind_group(
      device,
      pc.camera_uniform_bind_group_layout,
      frame_data.camera_buffer
    )

    vertex_buffer.bind_groups[1] = device.create_bind_group(
      label   = 'Model Transform Bind Group',
      layout  = pc.model_uniform_bind_group_layout,
      entries = [
        {
          'binding': 0,
          'resource': {
            'buffer': self.agent_transformation_buffer.unwrap(),
            'offset': 0,
            'size': self.agent_transformation_buffer.unwrap().size 
          }
        }
      ]
    )

    vertex_buffer.bind_groups[2] = device.create_bind_group(
      label   = 'Display Configuration Bind Group',
      layout  = pc.display_config_bind_group_layout,
      entries = [
        {
          'binding': 0,
          'resource': {
            'buffer':  frame_data.display_config_buffer,
            'offset': 0,
            'size': frame_data.display_config_buffer.size 
          }
        }
      ]
    )

  def _load_uniform_buffers(
    self,
    device: wgpu.GPUDevice, 
    scene: Scene,
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    queue: wgpu.GPUQueue = device.queue
    queue.write_buffer(frame_data.camera_buffer, 0, pc.camera_data)
    queue.write_buffer(frame_data.display_config_buffer, 0, create_array('i', [0]))

class AgentRenderer(GPURenderer):
  def __init__(self, builder: RendererBuilder | None = None) -> None:
    super().__init__()
    self._render_pipeline: wgpu.GPURenderPipeline
    self.builder = AgentRendererBuilder() if builder is None else builder

  @property
  def render_pipeline(self) -> wgpu.GPURenderPipeline:
    return self._render_pipeline

  def prepare(
    self, 
    device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh_data: MeshData, 
    scene: Scene,
    frame_data: PerFrameData
  ) -> PerFrameData:
    pc = PipelineConfiguration()
    self._render_pipeline = self.builder.build(
      device, 
      render_texture_format, 
      mesh_data, 
      scene, 
      pc, 
      frame_data
    )
    return frame_data

  def render(
    self, 
    render_pass: wgpu.GPURenderPassEncoder, 
    frame_data: PerFrameData,
    mesh_data: MeshData
  ) -> None:
    vertex_buffer: MeshBuffer = mesh_data.vertex_buffer.unwrap()
    render_pass.set_bind_group(0, vertex_buffer.bind_groups[0], [], 0, 99999)
    render_pass.set_bind_group(1, vertex_buffer.bind_groups[1], [], 0, 99999)
    render_pass.set_bind_group(2, vertex_buffer.bind_groups[2], [], 0, 99999)
    
    render_pass.set_vertex_buffer(
      slot   = 0, 
      buffer = vertex_buffer.vbo
    )

    render_pass.set_index_buffer(
      buffer       = vertex_buffer.ibo, 
      index_format = wgpu.IndexFormat.uint32 # type: ignore
    ) 

    render_pass.draw_indexed(
      index_count    = vertex_buffer.count, 
      instance_count = 1, 
      first_index    = 0, 
      base_vertex    = 0, 
      first_instance = 0
    )  