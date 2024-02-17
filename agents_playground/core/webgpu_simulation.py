import os
from pathlib import Path
import wx
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget
from agents_playground.cameras.camera import Camera

from agents_playground.core.observe import Observable
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.gpu.pipelines.landscape_pipeline import LandscapePipeline
from agents_playground.gpu.pipelines.obj_pipeline import ObjPipeline
from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline
from agents_playground.loaders.obj_loader import ObjLoader
from agents_playground.scene import Scene
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.context import SimulationContext
from agents_playground.spatial.landscape import cubic_tile_to_vertices
from agents_playground.spatial.mesh import MeshBuffer, MeshLike
from agents_playground.spatial.mesh.half_edge_mesh import HalfEdgeMesh, MeshWindingDirection
from agents_playground.spatial.mesh.printer import MeshGraphVizPrinter, MeshTablePrinter
from agents_playground.spatial.mesh.tesselator import FanTesselator, Tesselator
from agents_playground.spatial.mesh.triangle_mesh import TriangleMesh

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
    self._gpu_pipeline: WebGpuPipeline = LandscapePipeline()
    
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
    Starts the sim running.
    """

    """
    Steps
    1. Load the scene into memory (i.e. the Scene graph).
    2. Tesselate the landscape in landscape coordinates. This produces a VBO.
    3. Provide the landscape, landscape T/S/R matrix, camera, perspective matrix to the rendering pipeline.
    4. Render the scene.
      - vert shader
        - Transform the normals and vertices to world space.
        - Apply the camera view matrix and perspective.
      - Frag shader
        - Apply a lightning model. Use ambient light for now.
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
      # table_printer.print(landscape_lattice_mesh)

    # table_printer.print(landscape_lattice_mesh)
    # graph_printer.print(landscape_lattice_mesh)

    # 3. Tesselate the landscape.
    landscape_tri_mesh: MeshLike = landscape_lattice_mesh.deep_copy()
    # table_printer.print(landscape_tri_mesh)

    FanTesselator().tesselate(landscape_tri_mesh)
    # graph_printer.print(landscape_tri_mesh)

    # 4. Calculate the normals for the tessellated landscape mesh.
    landscape_tri_mesh.calculate_face_normals()
    landscape_tri_mesh.calculate_vertex_normals()

    # 5. Construct a VBO and VBI for the landscape.
    landscape_mesh_buffer: MeshBuffer = landscape_tri_mesh.pack()
    self._gpu_pipeline.mesh = landscape_mesh_buffer
    landscape_mesh_buffer.print()

    # scene_dir = 'poc/pyside_webgpu/pyside_webgpu/demos/obj/models'
    # scene_filename = 'skull.obj'
    # path = os.path.join(Path.cwd(), scene_dir, scene_filename)
    # model_data = ObjLoader().load(path)
    # mesh = TriangleMesh.from_obj(model_data) 
    # self._gpu_pipeline.mesh = mesh #type:ignore
    # mesh.print()

    # 6. Do some more stuff... Cameras, agents, etc..
    self._gpu_pipeline.camera = self.scene.camera

    # N. Initialize the graphics pipeline.
    # Note: The GPU pipe should ideally just know about vertex buffers.  
    self._gpu_pipeline.initialize_pipeline(self._canvas)

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