from typing import cast, Generator, Tuple

from more_itertools import first_true

from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.paths.circular_path import CirclePath
from agents_playground.project.extensions import register_task
from agents_playground.scene.scene import Scene
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger

from fsm_movement.movements import (
  BeingIdle,
  ClockwiseNavigation, 
  CounterClockwiseNavigation, 
  Movement, 
  Pulsing, 
  Resting, 
  SpinningClockwise, 
  SpinningCounterClockwise,
  UndefinedState
)

logger = get_default_logger()

class FindNextState(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

@register_task(label = 'agent_navigation')
def agent_navigation(*args, **kwargs) -> Generator:
  """A task that moves an agent along a circular path based on its internal state.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - starting_degree: Where on the circle to start the animation.
  """
  logger.info('Task: agent_traverse_circular_path - Initializing Task')
  scene: Scene = kwargs['scene']
  agent_id: Tag = kwargs['agent_id']
  path_id = kwargs['path_id']
  active_t: float = kwargs['starting_degree'] # In the range of [0, 360] degrees
  speed: float = kwargs['speed'] 

  agent: AgentLike = scene.agents[agent_id]
  path: CirclePath = cast(CirclePath, scene.paths[path_id])
  
  def find_next_state() -> None:
    raise FindNextState()

  movements: Tuple[Movement,...] = (
    BeingIdle(frames_active = 60, expired_action = find_next_state),
    ClockwiseNavigation(path, active_t, speed, frames_active = 120, expired_action = find_next_state),
    CounterClockwiseNavigation(path, active_t, speed, frames_active = 120, expired_action = find_next_state),
    SpinningClockwise(frames_active = 120, expired_action = find_next_state),
    SpinningCounterClockwise(frames_active = 120, expired_action = find_next_state),
    Pulsing(frames_active = 120, expired_action = find_next_state),
    Resting(frames_active = 120, expired_action = find_next_state),
  )
  
  undefined_state = UndefinedState()

  try:
    while True:
      movement: Movement = first_true(
        movements,
        default = undefined_state,
        pred = lambda movement: movement.appropriate(agent.agent_state.current_action_state.name)
      )
      try:
        movement.move(agent, scene)
      except FindNextState:
        movement.reset(agent)
        agent.agent_state.transition_to_next_action(agent.agent_characteristics())
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_traverse_circular_path - GeneratorExit')
  finally:
    logger.info('Task: agent_traverse_circular_path - Task Completed')