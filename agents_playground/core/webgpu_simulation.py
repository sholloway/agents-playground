from functools import partial
from math import radians
import os
from pathlib import Path

import wx
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.cameras.camera import Camera
from agents_playground.core.observe import Observable
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.fp import Something, SomethingMutator
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.landscape_pipeline import LandscapePipeline
from agents_playground.gpu.pipelines.obj_pipeline import ObjPipeline
from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline
from agents_playground.gpu.renderer_builders.simple_renderer_builder import assemble_camera_data
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.renderers.normals_renderer import NormalsRenderer
from agents_playground.gpu.renderers.simple_renderer import SimpleRenderer
from agents_playground.loaders.obj_loader import Obj, ObjLoader
from agents_playground.loaders.scene_loader import SceneLoader
from agents_playground.scene import Scene
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.context import SimulationContext
from agents_playground.spatial.landscape import cubic_tile_to_vertices
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.mesh import MeshBuffer, MeshData, MeshLike, MeshPacker, MeshRegistry
from agents_playground.spatial.mesh.half_edge_mesh import HalfEdgeMesh, MeshWindingDirection, obj_to_mesh
from agents_playground.spatial.mesh.packers.normal_packer import NormalPacker
from agents_playground.spatial.mesh.packers.simple_mesh_packer import SimpleMeshPacker
from agents_playground.spatial.mesh.printer import MeshGraphVizPrinter, MeshTablePrinter
from agents_playground.spatial.mesh.tesselator import FanTesselator, Tesselator
from agents_playground.spatial.mesh.triangle_mesh import TriangleMesh

def print_camera(camera: Camera) -> None:
  # Write a table of the Camera's location and focus.
  table_format  = '{:<20} {:<20} {:<20} {:<20}'
  header        = table_format.format('', 'X', 'Y', 'Z')
  loc_row       = table_format.format('Camera Location', camera.position.i, camera.position.j, camera.position.k)
  facing_row    = table_format.format('Facing', camera.facing.i, camera.facing.j, camera.facing.k) #type: ignore
  right_row     = table_format.format('Right', camera.right.i, camera.right.j, camera.right.k)     #type: ignore
  up_row        = table_format.format('Up', camera.up.i, camera.up.j, camera.up.k)                 #type: ignore
  target_row    = table_format.format('Target', camera.target.i, camera.target.j, camera.target.k) #type: ignore
  
  print('Camera Information')
  print(header)
  print(target_row)
  print(loc_row)
  print(facing_row)
  print(right_row)
  print(up_row)
  
def draw_frame(
  camera: Camera,
  canvas: WgpuWidget, 
  device: wgpu.GPUDevice,
  landscape_renderer: GPURenderer,
  normals_renderer: GPURenderer,
  frame_data: PerFrameData
):
  """
  The main render function. This is responsible for populating the queues of the 
  various rendering pipelines for all geometry that needs to be rendered per frame.

  It is bound to the canvas.
  """
  #1. Calculate the current aspect ratio.
  canvas_width, canvas_height = canvas.GetSize()
  aspect_ratio: float = canvas_width/canvas_height

  canvas_context: wgpu.GPUCanvasContext = canvas.get_context()
  current_texture: wgpu.GPUTexture = canvas_context.get_current_texture()

  # 2. Calculate the projection matrix.
  camera.projection_matrix = Matrix4x4.perspective(
      aspect_ratio= aspect_ratio, 
      v_fov = radians(72.0), 
      near = 0.1, 
      far = 100.0
    )
  camera_data = assemble_camera_data(camera)
  device.queue.write_buffer(frame_data.camera_buffer, 0, camera_data)
  
  # 3. Build a render pass color attachment.
  # struct.RenderPassColorAttachment
  color_attachment = {
    "view": current_texture.create_view(),
    "resolve_target": None,
    "clear_value": (0.9, 0.5, 0.5, 1.0),    # Clear to pink.
    "load_op": wgpu.LoadOp.clear,           # type: ignore
    "store_op": wgpu.StoreOp.store          # type: ignore
  }

  # 4. Create a depth texture for the Z-Buffer.
  depth_texture: wgpu.GPUTexture = device.create_texture(
    label  = 'Z Buffer Texture',
    size   = current_texture.size, 
    usage  = wgpu.TextureUsage.RENDER_ATTACHMENT, # type: ignore
    format = wgpu.enums.TextureFormat.depth24plus_stencil8 # type: ignore
  )
  depth_texture_view = depth_texture.create_view()

  # 5. Create a depth stencil attachment.
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

  # 6. Create a GPU command encoder.
  command_encoder: wgpu.GPUCommandEncoder = device.create_command_encoder()

  # 7. Encode the drawing instructions.
  # The first command to encode is the instruction to do a rendering pass.
  pass_encoder: wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
    color_attachments         = [color_attachment],
    depth_stencil_attachment  = depth_attachment
  )

  # Set the landscape rendering pipe line as the active one.
  # Encode the landscape drawing instructions.
  pass_encoder.set_pipeline(frame_data.landscape_render_pipeline)
  landscape_renderer.render(pass_encoder, frame_data)
  
  # Set the normals rendering pipe line as the active one.
  # Encode the normals drawing instructions.
  pass_encoder.set_pipeline(frame_data.normals_render_pipeline)
  normals_renderer.render(pass_encoder, frame_data)

  # Submit the draw calls to the GPU.
  pass_encoder.end()
  device.queue.submit([command_encoder.finish()])

class WebGPUSimulation(Observable):
  def __init__(
    self, 
    parent: wx.Window,
    canvas: WgpuWidget,
    scene_file: str, 
    scene_loader: SceneLoader
  ) -> None:
    super().__init__()
    self._canvas = canvas
    self._scene_file = scene_file
    self._scene_loader = scene_loader
    self.scene: Scene                # Assigned in the launch() method.
    self._render_texture_format: str # Assigned in the launch() method.
    self._mesh_registry = MeshRegistry()
    self._context: SimulationContext = SimulationContext()
    self._task_scheduler = TaskScheduler()
    self._pre_sim_task_scheduler = TaskScheduler()
    
    # The 0.1.0 version of this allows _sim_loop to be set to None.
    # In 0.2.0 let's try to use a Maybe Monad or something similar.
    # self._sim_loop: WGPUSimLoop = WGPUSimLoop(scheduler = self._task_scheduler)
    # self._sim_loop.attach(self)

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""
    # Skipping for the moment.
    # Fire a wx.PostEvent to force a UI redraw?..
    pass

  def bind_event_listeners(self, frame: wx.Panel) -> None:
    """
    Given a panel, binds event listeners.
    """
    frame.Bind(wx.EVT_CHAR, self._handle_key_pressed)

  def launch(self) -> None:
    """
    Starts the simulation running.
    """
    self.scene = self._scene_loader.load(self._scene_file)
    self._construct_landscape_mesh(self._mesh_registry, self.scene)
    self._construct_agent_meshes(self._mesh_registry, self.scene)
    self._initialize_graphics_pipeline(self._canvas)
    model_world_transform = Matrix4x4.identity() # Right now it's just the identity matrix, but that will need to change as more and more meshes are added.

    # Setup the Rendering Pipelines
    frame_data: PerFrameData = PerFrameData()
    self._prepare_landscape_renderer(frame_data, self._mesh_registry, self.scene.camera, model_world_transform)
    self._prepare_normals_renderer(frame_data, self._mesh_registry, self.scene.camera, model_world_transform)

    # Bind functions to key data structures.
    self._bound_draw_frame = partial(
      draw_frame, 
      self.scene.camera, 
      self._canvas, 
      self._device, 
      self._mesh_renderer, 
      self._normals_renderer, 
      frame_data
    )
    
    # Bind the draw function and render the first frame.
    self._canvas.request_draw(self._bound_draw_frame) 

  def _construct_landscape_mesh(self, mesh_registry: MeshRegistry, scene: Scene) -> None:
    # 1. Build a half-edge mesh of the landscape.
    mesh_registry.add_mesh(MeshData('landscape'))
    landscape_lattice_mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CW)
    for tile in scene.landscape.tiles.values():
      tile_vertices = cubic_tile_to_vertices(tile, self.scene.landscape.characteristics)
      landscape_lattice_mesh.add_polygon(tile_vertices)
    mesh_registry['landscape'].mesh = Something(landscape_lattice_mesh)

    # 2. Tesselate the landscape.
    landscape_tri_mesh: MeshLike = landscape_lattice_mesh.deep_copy()
    FanTesselator().tesselate(landscape_tri_mesh)

    # 4. Calculate the normals for the tessellated landscape mesh.
    landscape_tri_mesh.calculate_face_normals()
    landscape_tri_mesh.calculate_vertex_normals()
    
    mesh_registry.add_mesh(
      MeshData(
        'landscape_tri_mesh', 
        lod                     = 1, 
        mesh_previous_lod_alias = Something('landscape'),
        mesh                    = Something(landscape_tri_mesh),
        vertex_buffer           = Something(SimpleMeshPacker().pack(landscape_tri_mesh)),
        normals_buffer          = Something(NormalPacker().pack(landscape_tri_mesh))
      )
    )
    mesh_registry['landscape'].next_lod_alias = Something('landscape_tri_mesh')

  def _construct_agent_meshes(self, mesh_registry: MeshRegistry, scene: Scene) -> None:
    pass

  def _initialize_graphics_pipeline(self, canvas: WgpuWidget) -> None:
    # Initialize the graphics pipeline via WebGPU.
    self._adapter: wgpu.GPUAdapter = self._provision_adapter(canvas)
    self._device: wgpu.GPUDevice = self._provision_gpu_device(self._adapter)
    self._canvas_context: wgpu.GPUCanvasContext = canvas.get_context()

    # Set the GPUCanvasConfiguration to control how drawing is done.
    self._render_texture_format = self._canvas_context.get_preferred_format(self._device.adapter)
    self._canvas_context.configure(
      device       = self._device, 
      usage        = wgpu.flags.TextureUsage.RENDER_ATTACHMENT, # type: ignore
      format       = self._render_texture_format,
      view_formats = [],
      color_space  = 'bgra8unorm-srgb', 
      alpha_mode   = 'opaque'
    )

  def _prepare_landscape_renderer(
    self, 
    frame_data: PerFrameData, 
    mesh_registry: MeshRegistry, 
    camera: Camera, 
    model_world_transform: Matrix
  ) -> None:
    self._mesh_renderer: GPURenderer = SimpleRenderer()
    self._mesh_renderer.prepare(
      device                = self._device, 
      render_texture_format = self._render_texture_format, 
      mesh                  = mesh_registry['landscape_tri_mesh'].vertex_buffer.unwrap(), 
      camera                = camera,
      model_world_transform = model_world_transform,
      frame_data            = frame_data
    )
  
  def _prepare_normals_renderer(
    self, 
    frame_data: PerFrameData, 
    mesh_registry: MeshRegistry, 
    camera: Camera, 
    model_world_transform: Matrix
  ) -> None:
    self._normals_renderer: GPURenderer = NormalsRenderer()
    self._normals_renderer.prepare(
      device                = self._device, 
      render_texture_format = self._render_texture_format, 
      mesh                  = mesh_registry['landscape_tri_mesh'].normals_buffer.unwrap(),
      camera                = camera,
      model_world_transform = model_world_transform,
      frame_data            = frame_data
    )

  def _handle_key_pressed(self, event: wx.Event) -> None:
    """
    Handle when a user presses a button on their keyboard.
    """
    # TODO: Migrate the key handling logic in agents_playground/terminal/keyboard/key_interpreter.py
    # TODO: Expand to handle more than just A/D/W/S keys.
    """
    EXPLANATION
      ASCII key codes use a single bit position between upper and lower case so 
      x | 0x20 will force any key to be lower case.
    
    For example:
      A is 65 or 1000001
      32 -> 0x20 -> 100000
      1000001 | 100000 -> 1100001 -> 97 -> 'a'
    """
    key_str = chr(event.GetKeyCode() | 0x20) #type: ignore

    # A/D are -/+ On on the X-Axis
    # S/W are -/+ On on the Z-Axis
    match key_str: #type: ignore
      case 'a':
        self.scene.camera.position.i -= 1
        self.scene.camera.update()
        print_camera(self.scene.camera)
      case 'd':
        self.scene.camera.position.i += 1
        self.scene.camera.update()
        print_camera(self.scene.camera)
      case 'w':
        self.scene.camera.position.k += 1
        self.scene.camera.update()
        print_camera(self.scene.camera)
      case 's':
        self.scene.camera.position.k -= 1
        self.scene.camera.update()
        print_camera(self.scene.camera)
      case 'f':
        print_camera(self.scene.camera)
      case _:
        pass 
    self._canvas.request_draw()

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

