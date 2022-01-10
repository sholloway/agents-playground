from time import sleep

import dearpygui.dearpygui as dpg

from agents_playground.core.simulation import Simulation, SimulationState
from agents_playground.core.scheduler import JobScheduler
from agents_playground.core.time_utilities import MS_PER_SEC, UPDATE_BUDGET, TimeInMS, TimeInSecs, TimeUtilities

class EventBasedSimulation(Simulation):
  def __init__(self) -> None:
    super().__init__()
    self._scheduler: JobScheduler = JobScheduler()
    self.menu_items = {
      'display': {
        'stats': dpg.generate_uuid(),
      }
    }

    self._layers = {
      'stats': dpg.generate_uuid(),
    }

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
    stats = {}
    stats['start_of_cycle'] = TimeUtilities.now()
    time_to_render:TimeInMS = stats['start_of_cycle'] + UPDATE_BUDGET

    # Are there any tasks to do in this cycle?
    # If so, do them.
    search_window: TimeInMS = time_to_render - stats['start_of_cycle']
    stats['time_started_running_tasks'] = TimeUtilities.now()
    self._scheduler.run_due_jobs(search_window)
    stats['time_finished_running_tasks'] = TimeUtilities.now()
    
    # Is there any time until we need to render?
    # If so, then sleep until then.
    break_time: TimeInSecs = (time_to_render - TimeUtilities.now())/MS_PER_SEC
    if break_time > 0:
      sleep(break_time) 

    self._update_statistics(stats)
    self._sim_loop_tick(**data) # Update the scene graph and force a render.

  def _update_statistics(self, stats: dict[str, float]) -> None:
    self._fps_rate = dpg.get_frame_rate()
    utilization = round(((stats['time_finished_running_tasks'] - stats['time_started_running_tasks'])/UPDATE_BUDGET) * 100, 2)

    # This is will cause a render. Need to be smart with how these are grouped.
    # There may be a way to do all the scene graph manipulation and configure_item
    # calls in a single buffer.
    # TODO Look at https://dearpygui.readthedocs.io/en/latest/documentation/staging.html
    dpg.configure_item(item=self._stats['fps'], text=f'Frame Rate (Hz): {self._fps_rate}')
    dpg.configure_item(item=self._stats['utilization'], text=f'Utilization (%): {utilization}')    
  
  def _setup_menu_bar_ext(self) -> None:
    """Setup simulation specific menu items."""
    with dpg.menu(label="Display"):
      dpg.add_menu_item(
        label="Statistics", 
        callback=self._toggle_layer, 
        tag=self.menu_items['display']['stats'], 
        check=True, 
        default_value=True, 
        user_data=self._layers['stats'])
      
