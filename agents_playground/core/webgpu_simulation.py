from __future__ import annotations

from abc import abstractmethod
from array import array as create_array
from array import ArrayType
from dataclasses import dataclass
from math import radians
import os
from pathlib import Path
from typing import Dict, List, Protocol, Tuple, cast
from functools import partial

from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.loaders.mesh import Mesh
from agents_playground.loaders.triangle_mesh import TriangleMesh
from agents_playground.spatial.matrix import Matrix, MatrixOrder
from agents_playground.spatial.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector3d import Vector3d

import wx
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.core.webgpu_sim_loop import WGPUSimLoop
from agents_playground.loaders.obj_loader import Obj, ObjLoader
from agents_playground.core.observe import Observable
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.context import SimulationContext


class WebGPUSimulation(Observable):
  def __init__(
    self, 
    parent: wx.Window,
    canvas: WgpuWidget,
    scene_toml: str, 
    scene_reader = SceneReader(), 
    project_name: str = ''
  ) -> None:
    super().__init__()
    self._canvas = canvas
    self._scene_toml = scene_toml
    self._project_name = project_name
    self._scene_reader = scene_reader
    self._context: SimulationContext = SimulationContext()
    self._task_scheduler = TaskScheduler()
    self._pre_sim_task_scheduler = TaskScheduler()
    self._gpu_pipeline = WebGpuPipeline()
    

    # The 0.1.0 version of this allows _sim_loop to be set to None.
    # In 0.2.0 let's try to use a Maybe Monad or something similar.
    # self._sim_loop: WGPUSimLoop = WGPUSimLoop(scheduler = self._task_scheduler)
    # self._sim_loop.attach(self)

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""
    # Skipping for the moment.
    # Fire a wx.PostEvent to force a UI redraw?..
    pass

    
  def launch(self) -> None:
    """Opens the Simulation Window
    (At the moment starts rendering...)
    """
    self._gpu_pipeline.initialize_pipeline(self._canvas)

  def handle_aspect_ratio_change(self, canvas: WgpuWidget) -> None:
    canvas_width, canvas_height = canvas.get_physical_size() # Bug: this isn't resizing...
    print(canvas.GetSize())
    print(f"{canvas_width}, {canvas_height}")
    aspect_ratio: float = canvas_width/canvas_height
    self._gpu_pipeline.refresh_aspect_ratio(aspect_ratio)
    canvas.request_draw()

ENABLE_WGPU_TRACING = False 
def update_camera(
  camera: Camera3d, 
  x:float  | None = None, 
  y: float | None = None,
  z: float | None = None
) -> None:
  x = x if x is not None else camera.position.i
  y = y if y is not None else camera.position.j
  z = z if z is not None else camera.position.k

  camera.position = Vector3d(x, y, z)
  camera.update()

def load_shader(shader_path: str, name: str, device: wgpu.GPUDevice) -> wgpu.GPUShaderModule:
  with open(file = shader_path, mode = 'r') as filereader:
    shader_code = filereader.read()
  return device.create_shader_module(
    label = name,
    code  = shader_code
  )

def array_byte_size(a: ArrayType) -> int:
  """Finds the size, in bytes, of a given array."""
  return a.buffer_info()[1]*a.itemsize

def assemble_camera_data(camera: Camera) -> ArrayType:
  view_matrix = camera.view_matrix
  proj_matrix = camera.projection_matrix
  proj_view: Tuple = \
    proj_matrix.transpose().flatten(MatrixOrder.Row) + \
    view_matrix.flatten(MatrixOrder.Row)
  return create_array('f', proj_view)

def update_uniforms(
  device: wgpu.GPUDevice, 
  camera_buffer: wgpu.GPUBuffer, 
  camera: Camera3d) -> None:
  camera_data = assemble_camera_data(camera)
  device.queue.write_buffer(camera_buffer, 0, camera_data)

def draw_frame(
  camera: Camera,
  canvas: WgpuWidget, 
  device: wgpu.GPUDevice,
  renderer: GPURenderer,
  frame_data: PerFrameData
):

  canvas_width, canvas_height = canvas.GetSize()
  aspect_ratio: float = canvas_width/canvas_height

  canvas_context: wgpu.GPUCanvasContext = canvas.get_context()
  current_texture: wgpu.GPUTexture = canvas_context.get_current_texture()

  camera.projection_matrix = Matrix4x4.perspective(
      aspect_ratio= aspect_ratio, 
      v_fov = radians(72.0), 
      near = 0.1, 
      far = 100.0
    )
  camera_data = assemble_camera_data(camera)
  device.queue.write_buffer(frame_data.camera_buffer, 0, camera_data)
  
  # struct.RenderPassColorAttachment
  color_attachment = {
    "view": current_texture.create_view(),
    "resolve_target": None,
    # "clear_value": (0.5, 0.5, 0.5, 1),  # Clear to Gray.
    "clear_value": (0.9, 0.5, 0.5, 1),    # Clear to pink.
    "load_op": wgpu.LoadOp.clear,         # type: ignore
    "store_op": wgpu.StoreOp.store        # type: ignore
  }

  # Create a depth texture for the Z-Buffer.
  depth_texture: wgpu.GPUTexture = device.create_texture(
    label  = 'Z Buffer Texture',
    size   = [canvas_width, canvas_height, 1], 
    usage  = wgpu.TextureUsage.RENDER_ATTACHMENT, # type: ignore
    format = wgpu.enums.TextureFormat.depth24plus_stencil8 # type: ignore
  )
  depth_texture_view = depth_texture.create_view()

  depth_attachment = {
    "view": depth_texture_view,
    "depth_clear_value": 1.0,
    "depth_load_op": wgpu.LoadOp.clear,    # type: ignore
    "depth_store_op":  wgpu.StoreOp.store, # type: ignore
    "depth_read_only":  False,
    
    # I'm not sure about these values.
    "stencil_clear_value": 0,
    "stencil_load_op": wgpu.LoadOp.load,   # type: ignore
    "stencil_store_op": wgpu.StoreOp.store, # type: ignore
    "stencil_read_only": False,
  }

  command_encoder: wgpu.GPUCommandEncoder = device.create_command_encoder()

  # The first command to encode is the instruction to do a 
  # rendering pass.
  pass_encoder: wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
    color_attachments         = [color_attachment],
    depth_stencil_attachment  = depth_attachment
  )

  pass_encoder.set_pipeline(frame_data.render_pipeline)
  renderer.render(pass_encoder, frame_data)

  pass_encoder.end()
  device.queue.submit([command_encoder.finish()])

class WebGpuPipeline:
  """
  Orchestrate the WebGPU components.
  """
  def __init__(self) -> None:
    pass

  def initialize_pipeline(self, canvas: WgpuWidget) -> None:
    # Initialize WebGPU
    adapter: wgpu.GPUAdapter = self._provision_adapter(canvas)
    device: wgpu.GPUDevice = self._provision_gpu_device(adapter)
    if ENABLE_WGPU_TRACING:
      device.adapter.request_device_tracing('./wgpu_traces') # type: ignore
    canvas_context: wgpu.GPUCanvasContext = canvas.get_context()

    # Set the GPUCanvasConfiguration to control how drawing is done.
    render_texture_format = canvas_context.get_preferred_format(device.adapter)
    canvas_context.configure(
      device       = device, 
      usage        = wgpu.flags.TextureUsage.RENDER_ATTACHMENT, # type: ignore
      format       = render_texture_format,
      view_formats = [],
      color_space  = 'bgra8unorm-srgb', #'srgb',
      alpha_mode   = 'opaque'
    )

    # Load the 3D mesh into memory
    model_file_path = self._select_model()
    model_data: Obj = self._parse_model_file(model_file_path)
    mesh = TriangleMesh.from_obj(model_data)

    # Setup the Camera
    canvas_width, canvas_height = canvas.get_physical_size()
    aspect_ratio = canvas_width/canvas_height

    self._camera = Camera3d.look_at(
      position = Vector3d(3, 2, 4),
      target   = Vector3d(0, 0, 0),
      projection_matrix = Matrix4x4.perspective(
        aspect_ratio= aspect_ratio, 
        v_fov = radians(72.0), 
        near = 0.1, 
        far = 100.0
      ),
    )

    # Setup the Transformation Model.
    model_world_transform = Matrix4x4.identity()

    # Create a depth texture for the Z-Buffer.
    # depth_texture: wgpu.GPUTexture = device.create_texture(
    #   label  = 'Z Buffer Texture',
    #   size   = [canvas_width, canvas_height, 1], 
    #   usage  = wgpu.TextureUsage.RENDER_ATTACHMENT, # type: ignore
    #   format = wgpu.enums.TextureFormat.depth24plus_stencil8 # type: ignore
    # )

    # depth_texture_view = depth_texture.create_view()

    # Setup the Renderer
    renderer: GPURenderer = SimpleRenderer()

    # Prepare the per-frame data.
    frame_data: PerFrameData = renderer.prepare(
      device, 
      render_texture_format, 
      mesh,
      self._camera,
      model_world_transform
    )

    # Bind functions to key data structures.
    # self._bound_update_camera = partial(update_camera, cast(Camera3d,camera))
    self._bound_update_uniforms = partial(update_uniforms, device, frame_data.camera_buffer, self._camera) # type: ignore
    self._bound_draw_frame = partial(draw_frame, self._camera, canvas, device, renderer, frame_data)
    
    canvas.request_draw(self._bound_draw_frame)

  def refresh_aspect_ratio(self, aspect_ratio: float) -> None:
    self._camera.projection_matrix = Matrix4x4.perspective(
        aspect_ratio= aspect_ratio, 
        v_fov = radians(72.0), 
        near = 0.1, 
        far = 100.0
      )
    self._bound_update_uniforms()

  def _provision_adapter(self, canvas: wgpu.gui.WgpuCanvasInterface) -> wgpu.GPUAdapter:
    """
    Create a high performance GPUAdapter for a Canvas.
    """
    return wgpu.gpu.request_adapter( # type: ignore
      canvas=canvas, 
      power_preference='high-performance'
    ) 

  def _provision_gpu_device(self, adapter: wgpu.GPUAdapter) -> wgpu.GPUDevice:
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
  
  def _select_model(self) -> str:
    """
    Find the path for the desired scene.
    """
    scene_dir = 'poc/pyside_webgpu/pyside_webgpu/demos/obj/models'
    scene_filename = 'skull.obj'
    return os.path.join(Path.cwd(), scene_dir, scene_filename)
  
  def _parse_model_file(self, scene_file_path: str) -> Obj:
    return ObjLoader().load(scene_file_path)
  
@dataclass(init=False)
class PerFrameData:
  """
  Data class for grouping the things that can be updated by the client.
  """
  camera_buffer: wgpu.GPUBuffer
  vbo: wgpu.GPUBuffer
  ibo: wgpu.GPUBuffer
  vertex_normals_buffer: wgpu.GPUBuffer
  model_world_transform_buffer: wgpu.GPUBuffer
  display_config_buffer: wgpu.GPUBuffer
  num_primitives: int
  render_pipeline: wgpu.GPURenderPipeline
  camera_bind_group: wgpu.GPUBindGroup
  model_transform_bind_group: wgpu.GPUBindGroup
  display_config_bind_group: wgpu.GPUBindGroup
  
class GPURenderer(Protocol):
  def prepare(
    self, 
    device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh: Mesh, 
    camera: Camera,
    model_world_transform: Matrix
  ) -> PerFrameData:
    ...

  def render(
    self, 
    render_pass: wgpu.GPURenderPassEncoder, 
    frame_data: PerFrameData
  ) -> None:
    ...

class SimpleRenderer(GPURenderer):
  def __init__(self, builder: RendererBuilder | None = None) -> None:
    self.builder = SimpleRendererBuilder() if builder is None else builder

  def prepare(
    self, 
    device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh: Mesh, 
    camera: Camera,
    model_world_transform: Matrix
  ) -> PerFrameData:
    pc = PipelineConfiguration()
    frame_data = PerFrameData()
    return self.builder.build(
      device, 
      render_texture_format, 
      mesh, 
      camera, 
      model_world_transform, 
      pc, 
      frame_data
    )

  def render(
    self, 
    render_pass: wgpu.GPURenderPassEncoder, 
    frame_data: PerFrameData
  ) -> None:
    render_pass.set_bind_group(0, frame_data.camera_bind_group, [], 0, 99999)
    render_pass.set_bind_group(1, frame_data.model_transform_bind_group, [], 0, 99999)
    render_pass.set_bind_group(2, frame_data.display_config_bind_group, [], 0, 99999)
    
    render_pass.set_vertex_buffer(slot = 0, buffer = frame_data.vbo)
    render_pass.set_index_buffer(buffer = frame_data.ibo, index_format=wgpu.IndexFormat.uint32) # type: ignore

    render_pass.draw_indexed(
      index_count    = frame_data.num_primitives, 
      instance_count = 1, 
      first_index    = 0, 
      base_vertex    = 0, 
      first_instance = 0
    )  

@dataclass(init=False)
class PipelineConfiguration:
  """
  Simple data class used to group the various pipeline aspects.
  Intended to only be used inside of a renderer.
  """
  render_texture_format: str
  shader: wgpu.GPUShaderModule
  primitive_config: Dict
  vertex_config: Dict
  fragment_config: Dict
  camera_data: ArrayType
  model_world_transform_data: ArrayType
  camera_uniform_bind_group_layout: wgpu.GPUBindGroupLayout
  model_uniform_bind_group_layout: wgpu.GPUBindGroupLayout
  display_config_bind_group_layout: wgpu.GPUBindGroupLayout
  
class RendererBuilder(Protocol):
  def build(self, device: wgpu.GPUDevice, 
    render_texture_format: str, 
    mesh: Mesh, 
    camera: Camera,
    model_world_transform: Matrix,
    pc: PipelineConfiguration,
    frame_data: PerFrameData
  ) -> PerFrameData:
    self._load_shaders(device, pc)
    self._build_pipeline_configuration(render_texture_format, pc)
    self._load_mesh(device, mesh, frame_data)
    self._setup_camera(device, camera, pc, frame_data)
    self._setup_model_transform(device, model_world_transform, pc, frame_data)
    self._setup_uniform_bind_groups(device, pc, frame_data)
    self._setup_renderer_pipeline(device, pc, frame_data)
    self._create_bind_groups(device, pc, frame_data)
    self._load_uniform_buffers(device, pc, frame_data)
    return frame_data
  
  @abstractmethod
  def _load_shaders(self, device: wgpu.GPUDevice, pc: PipelineConfiguration) -> None:
    ...

  @abstractmethod
  def _build_pipeline_configuration(
    self, 
    render_texture_format: str,
    pc: PipelineConfiguration,
  ) -> None:
    ...

  @abstractmethod
  def _load_mesh(
    self, 
    device: wgpu.GPUDevice, 
    mesh: Mesh, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _setup_camera(
    self, 
    device: wgpu.GPUDevice, 
    camera: Camera, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _setup_model_transform(
    self,
    device: wgpu.GPUDevice, 
    model_world_transform: Matrix, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _setup_uniform_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration,
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _setup_renderer_pipeline(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _create_bind_groups(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

  @abstractmethod
  def _load_uniform_buffers(
    self,
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration, 
    frame_data: PerFrameData
  ) -> None:
    ...

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
    mesh: Mesh, 
    frame_data: PerFrameData
  ) -> None:
    # Load the 3D mesh into a GPUVertexBuffer.
    frame_data.vbo = self._mesh_config.create_vertex_buffer(device, mesh.vertices)
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
      label         = 'Rendering Pipeline', 
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

class MeshConfigurationBuilder:
  def configure_pipeline_primitives(self) -> Dict:
    """
    Specify what type of geometry should the GPU render.
    Returns a structs.PrimitiveState
    """
    primitive_config = {
      "topology":   wgpu.PrimitiveTopology.triangle_list, # type: ignore
      "front_face": wgpu.FrontFace.ccw, # type: ignore Note that the OBJ spec lists verts in ccw order.
      "cull_mode":  wgpu.CullMode.back, # type: ignore
    }
    return primitive_config

  def create_vertex_buffer(self, device: wgpu.GPUDevice, vertices: List[float]) -> wgpu.GPUBuffer:
    vbo_data = create_array('f', vertices)
    return device.create_buffer_with_data(
      label = 'Vertex Buffer',
      data  = vbo_data,
      usage = wgpu.BufferUsage.VERTEX # type: ignore
    )

  def create_vertex_normals_buffer(
    self,
    device: wgpu.GPUDevice,
    normals: List[float]
  ) -> wgpu.GPUBuffer:
    vertex_normals_data = create_array('f', normals)
    return device.create_buffer_with_data(
      label = 'Vertex Normals Buffer',
      data  = vertex_normals_data,
      usage = wgpu.BufferUsage.VERTEX # type: ignore
    )

  def create_index_buffer(
    self,
    device: wgpu.GPUDevice,
    indices: List[int]
  )-> wgpu.GPUBuffer:
    ibo_data = create_array('I', indices)
    return device.create_buffer_with_data(
      label = 'Index Buffer',
      data  = ibo_data,
      usage = wgpu.BufferUsage.INDEX # type: ignore
    )
  
class ShaderConfigurationBuilder:
  def configure_fragment_shader(self, render_texture_format, white_model_shader):
    """
    Returns a structs.FragmentState.
    """
    fragment_config = {
      "module": white_model_shader,
      "entry_point": "fs_main",
      "targets": [
        {
          "format": render_texture_format
        }
      ]
    }
    return fragment_config

  def configure_vertex_shader(self, white_model_shader):
    """
    Returns a structs.VertexState.
    """
    vertex_config = {
      "module": white_model_shader,
      "entry_point": "vs_main",
      "constants": {},
      "buffers": [ # structs.VertexBufferLayout
        {
          'array_stride': 4 * 4 + 4*3 + 4*3 + 4*3,       # Position (x,y,z,w), Texture (u,v,w), Normal(i,j,k), Barycentric(x,y,z)
          'step_mode': wgpu.VertexStepMode.vertex, # type: ignore
          'attributes': [                          # structs.VertexAttribute
            {
              'shader_location': 0,
              'format': wgpu.VertexFormat.float32x4, # type: ignore This is of the form: x,y,z,w
              'offset': 0
            },
            {
              'shader_location': 1,
              'format': wgpu.VertexFormat.float32x3, # type: ignore This is of the form: u, v, w
              'offset': 4 * 4 
            },
            {
              'shader_location': 2,
              'format': wgpu.VertexFormat.float32x3, # type: ignore This is of the form: i,j,k
              'offset': 4 * 4 + 4*3
            },
            {
              'shader_location': 3,
              'format': wgpu.VertexFormat.float32x3, # type: ignore This is of the form: x,y,j
              'offset': 4 * 4 + 4*3 + 4*3
            },
          ]
        }
      ],
    }
    return vertex_config
  
class CameraConfigurationBuilder:
  def create_model_ubg_layout(self, device: wgpu.GPUDevice):
    return device.create_bind_group_layout(
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

  def create_camera_ubg_layout(self, device:wgpu.GPUDevice) -> wgpu.GPUBindGroupLayout:
    return device.create_bind_group_layout(
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

  def create_camera_buffer(
    self,
    device: wgpu.GPUDevice,
    camera: Camera3d
  ) -> wgpu.GPUBuffer:
    camera_buffer_size = (4 * 16) + (4 * 16)
    return device.create_buffer(
      label = 'Camera Buffer',
      size = camera_buffer_size,
      usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST # type: ignore
    )

  def create_model_world_transform_buffer(
    self,
    device: wgpu.GPUDevice
  ) -> wgpu.GPUBuffer:
    return device.create_buffer(
      label = 'Model Transform Buffer',
      size = 4 * 16,
      usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST # type: ignore
    )

  def create_camera_bind_group(
    self,
    device: wgpu.GPUDevice,
    camera_uniform_bind_group_layout: wgpu.GPUBindGroupLayout,
    camera_buffer: wgpu.GPUBuffer
  ) -> wgpu.GPUBindGroup:
    return device.create_bind_group(
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

  def create_model_transform_bind_group(
    self,
    device: wgpu.GPUDevice,
    model_uniform_bind_group_layout: wgpu.GPUBindGroupLayout,
    model_world_transform_buffer: wgpu.GPUBuffer
  ) -> wgpu.GPUBindGroup:
    return device.create_bind_group(
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