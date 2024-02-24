from functools import partial
from math import radians

import wx
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget
from agents_playground.cameras.camera import Camera

from agents_playground.core.observe import Observable
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.landscape_pipeline import LandscapePipeline
from agents_playground.gpu.pipelines.normals_pipeline import NormalsPipeline
from agents_playground.gpu.pipelines.obj_pipeline import ObjPipeline
from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline
from agents_playground.gpu.renderer_builders.simple_renderer_builder import assemble_camera_data
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.renderers.simple_renderer import SimpleRenderer
from agents_playground.loaders.obj_loader import ObjLoader
from agents_playground.scene import Scene
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.context import SimulationContext
from agents_playground.spatial.landscape import cubic_tile_to_vertices
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.mesh import MeshBuffer, MeshLike, MeshPacker
from agents_playground.spatial.mesh.half_edge_mesh import HalfEdgeMesh, MeshWindingDirection
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
  facing_row    = table_format.format('Facing', camera.facing.i, camera.facing.j, camera.facing.k)
  right_row     = table_format.format('Right', camera.right.i, camera.right.j, camera.right.k)
  up_row        = table_format.format('Up', camera.up.i, camera.up.j, camera.up.k)
  target_row    = table_format.format('Target', camera.target.i, camera.target.j, camera.target.k)
  
  print('Camera Information')
  print(header)
  print(target_row)
  print(loc_row)
  print(facing_row)
  print(right_row)
  print(up_row)

def update_uniforms(
  device: wgpu.GPUDevice, 
  camera_buffer: wgpu.GPUBuffer, 
  camera: Camera) -> None:
  camera_data = assemble_camera_data(camera)
  device.queue.write_buffer(camera_buffer, 0, camera_data)
  
def draw_frame(
  camera: Camera,
  canvas: WgpuWidget, 
  device: wgpu.GPUDevice,
  renderer: GPURenderer,
  frame_data: PerFrameData
):
  """
  The main render function. This is responsible for populating the queues of the 
  various rendering pipelines for all geometry that needs to be rendered per frame.

  It is bound to the canvas.
  """
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
    "clear_value": (0.9, 0.5, 0.5, 1.0),    # Clear to pink.
    "load_op": wgpu.LoadOp.clear,           # type: ignore
    "store_op": wgpu.StoreOp.store          # type: ignore
  }

  # Create a depth texture for the Z-Buffer.
  depth_texture: wgpu.GPUTexture = device.create_texture(
    label  = 'Z Buffer Texture',
    size   = current_texture.size, 
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

class WebGPUSimulation(Observable):
  def __init__(
    self, 
    parent: wx.Window,
    canvas: WgpuWidget,
    scene_file: str, 
    scene_reader: SceneReader
  ) -> None:
    super().__init__()
    self._canvas = canvas
    self._scene_file = scene_file
    self._scene_reader = scene_reader
    self.scene: Scene # Assigned in the launch() method.
    self._context: SimulationContext = SimulationContext()
    self._task_scheduler = TaskScheduler()
    self._pre_sim_task_scheduler = TaskScheduler()
    # self._gpu_pipeline: WebGpuPipeline = ObjPipeline()
    self._landscape_pipeline: WebGpuPipeline = LandscapePipeline()
    self._normals_pipeline: WebGpuPipeline = NormalsPipeline()
    
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
    table_printer = MeshTablePrinter()
    graph_printer = MeshGraphVizPrinter()

    # 1. Load the scene into memory.
    self.scene = self._scene_reader.load(self._scene_file)

    # 2. Construct a half-edge mesh of the landscape.
    landscape_lattice_mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CW)
    for tile in self.scene.landscape.tiles.values():
      tile_vertices = cubic_tile_to_vertices(tile, self.scene.landscape.characteristics)
      landscape_lattice_mesh.add_polygon(tile_vertices)

    # 3. Tesselate the landscape.
    landscape_tri_mesh: MeshLike = landscape_lattice_mesh.deep_copy()
    FanTesselator().tesselate(landscape_tri_mesh)

    # 4. Calculate the normals for the tessellated landscape mesh.
    landscape_tri_mesh.calculate_face_normals()
    landscape_tri_mesh.calculate_vertex_normals()

    # 5. Construct a VBO and VBI for the landscape.
    landscape_mesh_buffer: MeshBuffer = SimpleMeshPacker().pack(landscape_tri_mesh)
    self._landscape_pipeline.mesh = landscape_mesh_buffer
    print('Mesh: Packed for GPU Pipeline')
    landscape_mesh_buffer.print()
    print('')

    # Construct a VBO and VBI for the landscape normals.
    # NOTE: This is just for debugging.
    # NOTE: Once the normals visualization is working, I should really make the 
    # skull load into a half-edge mesh. That would probably go a long way in 
    # verifying that the mesh implementation is correct and simplify further 
    # development.
    normals_mesh_buffer: MeshBuffer = NormalPacker().pack(landscape_tri_mesh)
    self._normals_pipeline.mesh = normals_mesh_buffer

    # 5. Use the Skull Model instead for debugging.
    # scene_dir = 'poc/pyside_webgpu/pyside_webgpu/demos/obj/models'
    # scene_filename = 'skull.obj'
    # path = os.path.join(Path.cwd(), scene_dir, scene_filename)
    # model_data = ObjLoader().load(path)
    # mesh = TriangleMesh.from_obj(model_data) 
    # self._landscape_pipeline.mesh = mesh #type:ignore
    # mesh.print()

    # 6. Initialize the graphics pipeline via WebGPU.
    adapter: wgpu.GPUAdapter = self._provision_adapter(self._canvas)
    device: wgpu.GPUDevice = self._provision_gpu_device(adapter)
    canvas_context: wgpu.GPUCanvasContext = self._canvas.get_context()

    # Enable Tracing when debugging...
    # wgpu.backends.wgpu_native.request_device_tracing(adapter, './wgpu_traces') 
  
    # 7. Set the GPUCanvasConfiguration to control how drawing is done.
    render_texture_format = canvas_context.get_preferred_format(device.adapter)
    canvas_context.configure(
      device       = device, 
      usage        = wgpu.flags.TextureUsage.RENDER_ATTACHMENT, # type: ignore
      format       = render_texture_format,
      view_formats = [],
      color_space  = 'bgra8unorm-srgb', 
      alpha_mode   = 'opaque'
    )

    # Setup the Transformation Model.
    # NOTE: This should be defined in the Scene file...
    # Right now it's just the identity matrix, but that will need to change as 
    # more and more meshes are added.
    model_world_transform = Matrix4x4.identity()

    # 8. Setup the Rendering Pipelines
    mesh_renderer: GPURenderer = SimpleRenderer()
    # TODO: Do something similar to the above line for the Normals renderer.

    # I need to think through the PerFrameData stuff. 
    # How does that change to support multiple meshes and multiple rendering pipelines?
    # I could be as simple as there is a landscape_vbo/vbi, and a mesh_rendering_pipeline, and a normals_pipeline...
    frame_data: PerFrameData = mesh_renderer.prepare(
      device, 
      render_texture_format, 
      landscape_mesh_buffer,
      self.scene.camera,
      model_world_transform
    )

    # 9. Bind functions to key data structures.
    self._bound_update_uniforms = partial(update_uniforms, device, frame_data.camera_buffer, self.scene.camera) 
    self._bound_draw_frame = partial(draw_frame, self.scene.camera, self._canvas, device, mesh_renderer, frame_data)
    
    # 10. Bind the draw function and render the first frame.
    self._canvas.request_draw(self._bound_draw_frame)

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

