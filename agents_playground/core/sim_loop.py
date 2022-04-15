
import threading
from time import sleep

import dearpygui.dearpygui as dpg

from agents_playground.agents.utilities import update_agent_in_scene_graph
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.time_utilities import MS_PER_SEC, UPDATE_BUDGET, TimeInMS, TimeInSecs, TimeUtilities
from agents_playground.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState

class SimLoop:
  """The main loop of a simulation."""
  def __init__(self, scheduler: TaskScheduler) -> None:
    self._task_scheduler = scheduler
    self._sim_stopped_check_time: float = 0.5
    self._sim_current_state: SimulationState = SimulationState.INITIAL

  @property
  def simulation_state(self) -> SimulationState:
    return self._sim_current_state

  @simulation_state.setter
  def simulation_state(self, next_state: SimulationState) -> None:
    self._sim_current_state = next_state

  def start(self, context: SimulationContext) -> None:
    """Create a thread for updating the simulation."""
    # Note: A daemonic thread cannot be "joined" by another thread. 
    # They are destroyed when the main thread is terminated.
    self._sim_thread = threading.Thread( 
      name="simulation-loop", 
      target=self._sim_loop, 
      args=(context,), 
      daemon=True
    )
    self._sim_thread.start()

  def _sim_loop(self, context: SimulationContext):
    """The thread callback that processes a simulation tick.
    
    Using the definitions in agents_playground.core.time_utilities, this ensures
    a fixed time for scheduled events to be ran. Rendering is handled automatically
    via DataPyUI (note: VSync is turned on when the Viewport is created.)

    For 60 FPS, TIME_PER_UPDATE is 5.556 ms.
    """
    while self.simulation_state is not SimulationState.ENDED:
      if self.simulation_state is SimulationState.RUNNING:
        self._process_sim_cycle(context)        
      else:
        # The sim isn't running so don't keep checking it.
        sleep(self._sim_stopped_check_time) 

  def _process_sim_cycle(self, context: SimulationContext) -> None:
    loop_stats = {}
    loop_stats['start_of_cycle'] = TimeUtilities.now()
    time_to_render:TimeInMS = loop_stats['start_of_cycle'] + UPDATE_BUDGET

    # Are there any tasks to do in this cycle? If so, do them.
    # task_time_window: TimeInMS = time_to_render - loop_stats['start_of_cycle']
    loop_stats['time_started_running_tasks'] = TimeUtilities.now()
    self._task_scheduler.queue_holding_tasks()
    self._task_scheduler.consume()
    loop_stats['time_finished_running_tasks'] = TimeUtilities.now()

    # Is there any time until we need to render?
    # If so, then sleep until then.
    break_time: TimeInSecs = (time_to_render - TimeUtilities.now())/MS_PER_SEC
    if break_time > 0:
      sleep(break_time) 

    self._update_statistics(loop_stats, context)
    self._update_render(context.scene)
    self._update_scene_graph(context.scene)

  def _update_statistics(self, stats: dict[str, float], context: SimulationContext) -> None:
    context.stats.fps.value = dpg.get_frame_rate()
    context.stats.utilization.value = round(((stats['time_finished_running_tasks'] - stats['time_started_running_tasks'])/UPDATE_BUDGET) * 100, 2)

    # This is will cause a render. Need to be smart with how these are grouped.
    # There may be a way to do all the scene graph manipulation and configure_item
    # calls in a single buffer.
    # TODO Look at https://dearpygui.readthedocs.io/en/latest/documentation/staging.html
    dpg.configure_item(item=context.stats.fps.id, text=f'Frame Rate (Hz): {context.stats.fps.value}')
    dpg.configure_item(item=context.stats.utilization.id, text=f'Utilization (%): {context.stats.utilization.value}')  

  def _update_render(self, scene: Scene) -> None: 
    for agent in filter(lambda a: a.agent_render_changed, scene.agents.values()):
      dpg.configure_item(agent.render_id, fill = agent.crest)
    
  def _update_scene_graph(self, scene: Scene) -> None:
    for agent_id, agent in scene.agents.items():
      update_agent_in_scene_graph(agent, agent_id, scene.cell_size)
