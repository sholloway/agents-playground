import wx
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.core.observe import Observable
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.gpu.pipelines.obj_pipeline import ObjPipeline
from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline
from agents_playground.scene import Scene
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.context import SimulationContext
from agents_playground.spatial.mesh import Mesh
from agents_playground.spatial.mesh.tesselator import Tesselator

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
    self._gpu_pipeline: WebGpuPipeline = ObjPipeline()
    
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
    scene: Scene = self._scene_reader.load(self._scene_file)

    landscape_mesh: Mesh = Tesselator.from_landscape(scene.landscape)

    # Note: The GPU pipe should ideally just know about vertex buffers.  
    self._gpu_pipeline.initialize_pipeline(self._canvas)