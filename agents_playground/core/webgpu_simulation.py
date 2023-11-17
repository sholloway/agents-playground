import wx
import wgpu
import wgpu.backends.rs
from agents_playground.ui.wx_patch import WgpuWidget

from agents_playground.core.observe import Observable
from agents_playground.core.sim_loop import SimLoop
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState

class WebGPUSimulation(Observable):
  def __init__(
    self, 
    parent: wx.Window,
    scene_toml: str, 
    scene_reader = SceneReader(), 
    project_name: str = ''
  ) -> None:
    super().__init__()
    self._scene_toml = scene_toml
    self._project_name = project_name
    self._scene_reader = scene_reader

    self.canvas = WgpuWidget(parent)
    self.canvas.SetMinSize((640, 640))

    # Eventually need to fold these in...
    self._context: SimulationContext = SimulationContext()
    self._task_scheduler = TaskScheduler()
    self._pre_sim_task_scheduler = TaskScheduler()
    # The 0.1.0 version of this allows _sim_loop to be set to None.
    # In 0.2.0 let's try to use a Maybe Monad or something similar.
    # self._sim_loop: SimLoop | None = SimLoop(scheduler = self._task_scheduler)
    # self._sim_loop.attach(self)

    
    

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""
    # Skipping for the moment.
    pass

    
  def launch(self) -> None:
    """Opens the Simulation Window"""
    pass
