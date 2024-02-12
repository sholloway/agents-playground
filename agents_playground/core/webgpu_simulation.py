import wx
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.core.observe import Observable
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.gpu.pipelines.landscape_pipeline import LandscapePipeline
from agents_playground.gpu.pipelines.obj_pipeline import ObjPipeline
from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline
from agents_playground.scene import Scene
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.context import SimulationContext
from agents_playground.spatial.landscape import cubic_tile_to_vertices
from agents_playground.spatial.mesh import MeshBuffer, MeshLike
from agents_playground.spatial.mesh.half_edge_mesh import HalfEdgeMesh, MeshWindingDirection
from agents_playground.spatial.mesh.printer import MeshGraphVizPrinter, MeshTablePrinter
from agents_playground.spatial.mesh.tesselator import FanTesselator, Tesselator

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
    scene: Scene = self._scene_reader.load(self._scene_file)

    # 2. Construct a half-edge mesh of the landscape.
    landscape_lattice_mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CW)
    for tile in scene.landscape.tiles.values():
      tile_vertices = cubic_tile_to_vertices(tile, scene.landscape.characteristics)
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
   
    # 6. Do some more stuff... Cameras, agents, etc..
    self._gpu_pipeline.camera = scene.camera

    # N. Initialize the graphics pipeline.
    # Note: The GPU pipe should ideally just know about vertex buffers.  
    self._gpu_pipeline.initialize_pipeline(self._canvas)