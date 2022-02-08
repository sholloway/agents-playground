from time import sleep

import dearpygui.dearpygui as dpg

from agents_playground.core.simulation import Simulation, SimulationState
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.time_utilities import (
  MS_PER_SEC, 
  UPDATE_BUDGET, 
  TimeInMS, 
  TimeInSecs, 
  TimeUtilities)

class TaskBasedSimulation(Simulation):
  def __init__(self) -> None:
    super().__init__()
    self._task_scheduler = TaskScheduler()

  def _sim_loop(self, **data):
    """The thread callback that processes a simulation tick.
    
    Using the definitions in agents_playground.core.time_utilities, this ensures
    a fixed time for scheduled events to be ran. Rendering is handled automatically
    via DataPyUI (note: VSync is turned on when the Viewport is created.)

    For 60 FPS, TIME_PER_UPDATE is 5.556 ms.
    """
    while self.simulation_state is not SimulationState.ENDED:
      if self.simulation_state is SimulationState.RUNNING:
        self._process_sim_cycle(**data)        
      else:
        # The sim isn't running so don't keep checking it.
        sleep(self._sim_stopped_check_time) 

  def _process_sim_cycle(self, **data) -> None:
    loop_stats = {}
    loop_stats['start_of_cycle'] = TimeUtilities.now()
    time_to_render:TimeInMS = loop_stats['start_of_cycle'] + UPDATE_BUDGET

    # Are there any tasks to do in this cycle? If so, do them.
    # search_window: TimeInMS = time_to_render - loop_stats['start_of_cycle']
    loop_stats['time_started_running_tasks'] = TimeUtilities.now()
    self._task_scheduler.consume()
    loop_stats['time_finished_running_tasks'] = TimeUtilities.now()
    
    # Is there any time until we need to render?
    # If so, then sleep until then.
    break_time: TimeInSecs = (time_to_render - TimeUtilities.now())/MS_PER_SEC
    if break_time > 0:
      sleep(break_time) 

    self._update_statistics(loop_stats)
    self._sim_loop_tick(**data) # Update the scene graph and force a render.
  
  def _setup_menu_bar_ext(self) -> None:
    """Setup simulation specific menu items."""
    pass