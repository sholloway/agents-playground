from abc import abstractmethod
from math import copysign, radians
from types import SimpleNamespace
from typing import  Callable, List, Protocol
from typing import cast, Generator, Tuple

import dearpygui.dearpygui as dpg
from more_itertools import first_true
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.core.constants import DEFAULT_FONT_SIZE
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.project.extensions import register_entity, register_renderer, register_task
from agents_playground.renderers.color import Colors
from agents_playground.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext, Size
from agents_playground.simulation.tag import Tag

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

@register_entity(label='agent_state_display_refresh')
def agent_state_display_refresh(self: SimpleNamespace, scene: Scene) -> None:
  """
  Update function for the state_displays entities.

  Args:
  - self: A bound entity. 
  - scene: The active simulation scene.
  """
  agent: AgentLike = scene.agents[self.agent_id]
  state_name: str = agent.agent_state.current_action_state.name
  dpg.configure_item(item = self.id, text = f'State: {state_name}')

class Movement(Protocol):
  appropriate_states: List[str]
  active_counter: Counter

  def appropriate(self, state_name: str) -> bool:
    return state_name in self.appropriate_states

  def move(self, agent: AgentLike, scene: Scene) -> None:
    """Apply the active movement to the agent."""
    self._move(agent, scene)
    self.active_counter.decrement()

  def reset(self, agent: AgentLike) -> None:
    """Reset the active counter and undo any temporary changes to the agent."""
    self.active_counter.reset()
    self._reset_agent(agent)
  
  @abstractmethod
  def _move(self, agent: AgentLike, scene: Scene) -> None:
    ...

  def _reset_agent(self, agent:AgentLike) -> None:
    return
  
class BeingIdle(Movement):
  def __init__(
    self, 
    frames_active: int, 
    expired_action: Callable
  ) -> None:
    self.appropriate_states = ['IDLE_STATE']
    self.active_counter = CounterBuilder.integer_counter_with_defaults(
      start = frames_active, 
      min_value = 0, 
      min_value_reached = expired_action
    )

  def _move(self, agent: AgentLike, scene: Scene) -> None:
    return
  
class UndefinedState(Movement):
  def __init__(self) -> None:
    self.appropriate_states = ['']
    self.active_counter = CounterBuilder.count_up_from_zero()

  def _move(self, agent: AgentLike, scene: Scene) -> None:
    return  

class SpinningClockwise(Movement):
  def __init__(
    self, 
    frames_active: int, 
    expired_action: Callable,
    rotation_amount: float = radians(5)
  ) -> None:
    self.appropriate_states = ['SPINNING_CW']
    self.active_counter = CounterBuilder.integer_counter_with_defaults(
      start = frames_active, 
      min_value = 0, 
      min_value_reached = expired_action
    )
    self._direction = 1
    self._rotation_amount = rotation_amount

  def _move(self, agent: AgentLike, scene: Scene) -> None:
    new_orientation = agent.position.facing.rotate(self._rotation_amount * self._direction)
    agent.face(new_orientation, scene.cell_size)

@register_renderer(label='text_display')
def text_display(self: SimpleNamespace, context: SimulationContext) -> None:
  """Renders text for an entity state display.
  
  Args:
    - self: An entity is dynamically bound to the render function.
    - context: The simulation context for the running sim.
  """
  # Convert the specified location on the entity from cell coordinates to pixels.
  cell_size:Size = context.scene.cell_size
  location_in_pixels: Tuple[int,int] = (
    self.location[0] * cell_size.width, 
    self.location[1] * cell_size.height
  )

  agent: AgentLike = context.scene.agents[self.agent_id]
  state_name: str = agent.agent_state.current_action_state.name
  dpg.draw_text(
    tag = self.id, 
    pos = location_in_pixels, 
    size  = DEFAULT_FONT_SIZE,
    text = f'State: {state_name}')
  
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
  agent: AgentLike = scene.agents[agent_id]
  
  def find_next_state() -> None:
    raise FindNextState()

  movements: Tuple[Movement,...] = (
    BeingIdle(frames_active = 60, expired_action = find_next_state),
    SpinningClockwise(frames_active = 120, expired_action = find_next_state)
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

@register_renderer(label='render_agents_view_frustum')
def render_agents_view_frustum(**data) -> None:
  context: SimulationContext = data['context']
  scene: Scene = context.scene
  agent: AgentLike

  agents: List[AgentLike] = list(
    filter(
      lambda agent: agent.identity.toml_id != 1, 
      scene.agents.values()
    )
  )

  for agent in agents:
    dpg.draw_polyline(
      tag = cast(int, agent.identity.frustum_id), 
      points = [
        [*agent.physicality.frustum.vertices[0].coordinates], 
        [*agent.physicality.frustum.vertices[1].coordinates], 
        [*agent.physicality.frustum.vertices[2].coordinates], 
        [*agent.physicality.frustum.vertices[3].coordinates]
      ],
      closed = True,
      color=Colors.crimson.value, 
      thickness=agent.style.stroke_thickness
    )

@register_renderer(label='render_single_agent_view_frustum')
def render_single_agent_view_frustum(**data) -> None:
  context: SimulationContext = data['context']
  scene: Scene = context.scene
  agent: AgentLike

  primary_agents: List[AgentLike] = list(
    filter(
      lambda agent: agent.identity.toml_id == 1, 
      scene.agents.values()
    )
  )

  for agent in primary_agents:
    dpg.draw_polyline(
      tag = cast(int, agent.identity.frustum_id), 
      points = [
        [*agent.physicality.frustum.vertices[0].coordinates], 
        [*agent.physicality.frustum.vertices[1].coordinates], 
        [*agent.physicality.frustum.vertices[2].coordinates], 
        [*agent.physicality.frustum.vertices[3].coordinates]
      ],
      closed = True,
      color=Colors.crimson.value, 
      thickness=agent.style.stroke_thickness
    )

