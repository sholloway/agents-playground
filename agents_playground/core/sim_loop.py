
from enum import Enum
import threading
from typing import Callable, cast

import dearpygui.dearpygui as dpg

from agents_playground.agents.utilities import update_all_agents_display
from agents_playground.core.counter import Counter
from agents_playground.core.observe import Observable
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.time_utilities import MS_PER_SEC, UPDATE_BUDGET, TimeInMS, TimeInSecs, TimeUtilities
from agents_playground.core.waiter import Waiter
from agents_playground.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState
from agents_playground.simulation.statistics import Sample

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

class SimLoopEvent(Enum):
  UTILITY_SAMPLES_COLLECTED = 'UTILITY_SAMPLES_COLLECTED'

Frame = int
UtilityUtilizationWindow: Frame = 10

class SimLoop(Observable):
  """The main loop of a simulation."""
  def __init__(self, scheduler: TaskScheduler = TaskScheduler(), waiter = Waiter()) -> None:
    super().__init__()
    self._task_scheduler = scheduler
    self._sim_stopped_check_time: TimeInSecs = 0.5
    self._waiter = waiter
    self._sim_current_state: SimulationState = SimulationState.INITIAL
    self._utility_sampler = Counter(
      start = UtilityUtilizationWindow, 
      decrement_step=1,
      min_value = 0, 
      min_value_reached=self._utility_samples_collected)

  def __del__(self) -> None:
    logger.info('SimLoop deleted.')

  @property
  def simulation_state(self) -> SimulationState:
    return self._sim_current_state

  @simulation_state.setter
  def simulation_state(self, next_state: SimulationState) -> None:
    self._sim_current_state = next_state

  def end(self) -> None:
    self._sim_current_state = SimulationState.ENDED
    if hasattr(self, '_sim_thread'):
      self._sim_thread.join()

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
        self._waiter.wait(self._sim_stopped_check_time) 

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
    self._waiter.wait_until_deadline(time_to_render) 

    self._update_statistics(loop_stats, context)
    self._update_render(context.scene)
    self._utility_sampler.decrement()

  def _update_statistics(self, stats: dict[str, float], context: SimulationContext) -> None:
    context.stats.fps.value = dpg.get_frame_rate()
    frame_utilization_percentage: float = ((stats['time_finished_running_tasks'] - stats['time_started_running_tasks'])/UPDATE_BUDGET) * 100
    context.stats.utilization_sample = cast(Sample, round(frame_utilization_percentage, 2))

    # This is will cause a render. Need to be smart with how these are grouped.
    # There may be a way to do all the scene graph manipulation and configure_item
    # calls in a single buffer.
    # TODO Look at https://dearpygui.readthedocs.io/en/latest/documentation/staging.html
    dpg.configure_item(item=context.stats.fps.id, text=f'Frame Rate (Hz): {context.stats.fps.value}')
    dpg.configure_item(item=context.stats.utilization.id, text=f'Utilization (%): {context.stats.utilization.value}')  

  def _update_render(self, scene: Scene) -> None:
    for _, entity_grouping in scene.entities.items():
      for _, entity in entity_grouping.items():
        entity.update(scene)

    """
    TODO: Move this to an 'update_method' style function on Agent. 
    Perhaps there needs to be a default update function on Agent that can be 
    overridden. That may be putting the cart before the horse. Can the update_agent_in_scene_graph
    be merged with the configure_item call? It would be nice to simplify.

    Currently we're doing two passes over scene.agents and in the loop below the 
    SimLoop has knowledge of how to render an Agent. That's not good separation 
    of concerns.
    """
    update_all_agents_display(scene)

  def _utility_samples_collected(self) -> None:
    super().notify(SimLoopEvent.UTILITY_SAMPLES_COLLECTED.value)
    self._utility_sampler.reset()