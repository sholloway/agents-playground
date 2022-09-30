from __future__ import annotations

from enum import Enum
from functools import wraps
import os
import threading
from typing import Dict, List

from agents_playground.agents.utilities import update_all_agents_display
from agents_playground.core.constants import UPDATE_BUDGET
from agents_playground.core.counter import Counter
from agents_playground.core.observe import Observable
from agents_playground.core.simulation_performance import SimulationPerformance
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import Count, TimeInMS, TimeInSecs
from agents_playground.core.waiter import Waiter
from agents_playground.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState
from agents_playground.simulation.statistics import Sample

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

UTILITY_UTILIZATION_WINDOW: Count = 10
HARDWARE_SAMPLING_WINDOW: Count = 120

class SimLoopEvent(Enum):
  UTILITY_SAMPLES_COLLECTED = 'UTILITY_SAMPLES_COLLECTED'
  HARDWARE_SAMPLES_COLLECTED = 'FRAME_COMPLETE'

"""
I want to simplify the SimLoop._process_sim_cycle by removing the stat collection
code and putting it into a generic decoration.

Needs:
- Collect duration times for decorated methods.
- Collect a sequence of samples (e.g. frame utility)
"""
class MetricsCollector:
  def __init__(self) -> None:
    self.__samples: Dict[str, List[Sample]] = dict()

  def collect(self, metric_name, sample: Sample) -> None:
    """Collect samples as a series."""
    if metric_name not in self.__samples:
      self.__samples[metric_name] = []
    self.__samples[metric_name].append(sample)

  def sample(self, metric_name, sample_value: Sample) -> None:
    """Record a single value sample."""
    self.__samples[metric_name] = sample_value

  @property
  def samples(self) -> Dict[str, List[Sample]]:
    return self.__samples

  def clear(self) -> None:
    self.__samples.clear()

metrics = MetricsCollector()

def sample(sample_name:str):
  def decorator_sample(func) -> None:
    @wraps(func)
    def wrapper_sample(*args, **kargs):
      start: TimeInMS = TimeUtilities.now()
      result = func(*args, **kargs)
      end: TimeInMS = TimeUtilities.now()
      duration: TimeInMS = end - start
      metrics.collect(sample_name, duration)
      return result
    return wrapper_sample
  return decorator_sample

class SimLoop(Observable):
  """The main loop of a simulation."""
  def __init__(self, scheduler: TaskScheduler = TaskScheduler(), waiter = Waiter()) -> None:
    super().__init__()
    self._task_scheduler = scheduler
    self._sim_stopped_check_time: TimeInSecs = 0.5
    self._waiter = waiter
    self._sim_current_state: SimulationState = SimulationState.INITIAL
    self.__sim_started_time: TimeInSecs; 
    self._utility_sampler = Counter(
      start = UTILITY_UTILIZATION_WINDOW, 
      decrement_step=1,
      min_value = 0, 
      min_value_reached=self._utility_samples_collected)
    self._hardware_sampler = Counter(
      start = HARDWARE_SAMPLING_WINDOW, 
      decrement_step=1,
      min_value = 0, 
      min_value_reached=self._hardware_samples_collected)

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
    self.__sim_started_time = TimeUtilities.now_sec()
    while self.simulation_state is not SimulationState.ENDED:
      if self.simulation_state is SimulationState.RUNNING:
        self._process_sim_cycle(context)        
      else:
        # The sim isn't running so don't keep checking it.
        self._wait_until_next_frame()
      self._utility_sampler.decrement(frame_context = context)
      self._hardware_sampler.decrement(frame_context = context)

  @sample(sample_name='frame-tick')
  def _process_sim_cycle(self, context: SimulationContext) -> None:
    loop_stats = {}
    loop_stats['start_of_cycle'] = TimeUtilities.now()
    time_to_render:TimeInMS = loop_stats['start_of_cycle'] + UPDATE_BUDGET

    # Are there any tasks to do in this cycle? If so, do them.
    self._process_per_frame_tasks()

    # Is there any time until we need to render?
    # If so, then sleep until then.
    self._waiter.wait_until_deadline(time_to_render) 
    self._update_render(context.scene)

  @sample(sample_name='waiting-until-next-frame')
  def _wait_until_next_frame(self) -> None:
    self._waiter.wait(self._sim_stopped_check_time)     

  @sample(sample_name='running-tasks')
  def _process_per_frame_tasks(self) -> None:
    self._task_scheduler.queue_holding_tasks()
    self._task_scheduler.consume()
   
  @sample(sample_name='rendering')
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

  def _hardware_samples_collected(self, **kargs) -> None:
    context = kargs['frame_context']
    context.stats.hardware_metrics = SimulationPerformance.collect(self.__sim_started_time)
    super().notify(SimLoopEvent.HARDWARE_SAMPLES_COLLECTED.value)
  
  def _utility_samples_collected(self, **kargs) -> None:  
    """
    I'd like to use this hook to copy the samples to the context (eventually context.stats)
    and use the update method on the Simulation to grab the samples.

    1. copy the samples to the context
    2. Clear the SAMPLE dict.
    3. Notify the Simulation
    4. Reset the counter.

    Challenges
    - How to access the context instance? Context is not currently bound 
      to the counter or SimLoop.
    """
    context = kargs['frame_context']
    context.stats.samples = metrics.samples
    super().notify(SimLoopEvent.UTILITY_SAMPLES_COLLECTED.value)
    metrics.clear()
    self._utility_sampler.reset()



