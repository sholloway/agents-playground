from abc import abstractmethod
import itertools
from math import copysign, radians
from types import SimpleNamespace
from typing import  Callable, Dict, List, Protocol
from typing import cast, Generator, Tuple

import dearpygui.dearpygui as dpg
from more_itertools import first_true
from agents_playground.agents.byproducts.sensation import SensationType
from agents_playground.agents.memory.memory import Memory
from agents_playground.agents.memory.memory_container import MemoryContainer
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.systems.agent_visual_system import VisualSensation
from agents_playground.agents.utilities import render_deselected_agent, render_selected_agent
from agents_playground.containers.ttl_store import TTLStore
from agents_playground.core.constants import DEFAULT_FONT_SIZE
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp.containers import FPList
from agents_playground.legacy.project.extensions import register_entity, register_renderer, register_task
from agents_playground.renderers.color import BasicColors, ColorUtilities, Colors
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext, Size
from agents_playground.simulation.tag import Tag

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

@register_task(label='assign_agent_memory_model')
def assign_agent_memory_model(*args, **kwargs) -> None:
  logger.info('Task(assign_agent_memory_model): Starting task.')
  scene: Scene = kwargs['scene']
  for agent in scene.agents.values():
    agent.memory.add('sensory_memory', MemoryContainer(FPList[Memory]()))
    agent.memory.add('working_memory', MemoryContainer(TTLStore[Memory]()))
    agent.memory.add('long_term_memory', MemoryContainer(FPList[Memory]()))

@register_entity(label='agent_state_display_refresh')
def agent_state_display_refresh(self: SimpleNamespace, scene: Scene) -> None:
  """
  Update function for the state_displays entities.

  Args:
  - self: A bound entity. 
  - scene: The active simulation scene.
  """
  agent: AgentLike = scene.agents[self.agent_id]
  display: str = build_agent_memory_display(agent)
  if dpg.does_item_exist(item = self.id):
    dpg.configure_item(item = self.id, text = display)

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

def build_agent_memory_display(agent: AgentLike) -> str:
  display = f"""
  State: {agent.agent_state.current_action_state.name}
  
  Sensory Memory:
  {agent.memory['sensory_memory'].unwrap()}
  
  Working Memory:
  {agent.memory['working_memory'].unwrap()}
  
  Long Term Memory:
  {agent.memory['long_term_memory'].unwrap()}
  """
  return display

@register_renderer(label='display_agent_internals')
def display_agent_internals(self: SimpleNamespace, context: SimulationContext) -> None:
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
  display: str = build_agent_memory_display(agent)

  dpg.draw_text(
    tag  = self.id, 
    pos  = location_in_pixels, 
    size = DEFAULT_FONT_SIZE,
    text = display
  )
  
class FindNextState(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

@register_task(label = 'agent_navigation')
def agent_navigation(*args, **kwargs) -> Generator:
  """This task rotates and agent around its center of mass. 

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - agent_id: The scene ID of the agent to work on.
  """
  logger.info('Task: agent_traverse_circular_path - Initializing Task')
  scene: Scene = kwargs['scene']
  agent_id: Tag = kwargs['agent_id']
  agent: AgentLike = scene.agents[agent_id]
  
  def find_next_state() -> None:
    raise FindNextState()

  # Note: In this sim, the agent is evaluating it's next state every single 
  # tick of the simulation.
  movements: Tuple[Movement,...] = (
    BeingIdle(frames_active = 3, expired_action = find_next_state),
    SpinningClockwise(frames_active = 1, expired_action = find_next_state)
  )
  
  undefined_state = UndefinedState()
  seen_agents: List[AgentLike] = []  

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
        other_agents = find_other_agents(scene, agent_id)
        deselect_agents(seen_agents)
        seen_agents.clear()
        # agent.memory.sensory_memory.forget_all() # TODO: Shift this to be counter based.
        agent.memory['sensory_memory'].unwrap().clear()
        agent.transition_state(other_agents)
        agent.internal_systems.clear_byproducts()
        seen_agents = get_the_seen_agents(agent, other_agents)
        select_seen_agents(seen_agents)
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_traverse_circular_path - GeneratorExit')
  finally:
    logger.info('Task: agent_traverse_circular_path - Task Completed')

def select_seen_agents(seen_agents: List[AgentLike]):
  """Draw all of the "seen" agents as highlighted."""
  seen_agent: AgentLike
  for seen_agent in seen_agents:
    seen_agent.select()
    render_selected_agent(
      seen_agent.identity.render_id, 
      ColorUtilities.invert(seen_agent.style.fill_color)
    )

def get_the_seen_agents(agent: AgentLike, other_agents: Dict[Tag, AgentLike]):
  sensation: Memory
  seen_memories = [
    sensation.unwrap() for sensation in agent.memory['sensory_memory'].unwrap()
    if sensation.unwrap().type == SensationType.Visual
  ]

  # Produces [[tag, tag], [tag, tag]]
  seen_agent_ids = [
    cast(VisualSensation,sensation).seen 
    for sensation in seen_memories
  ]

  # Flatten the 2D list into a 1D list. [tag, tag, tag, tag]
  seen_agent_ids = [
    seen_id 
    for seen_list in seen_agent_ids
    for seen_id in seen_list 
  ]

  seen_agents = [
    agent 
    for agent in other_agents.values()
    if agent.identity.id in seen_agent_ids
  ]
    
  return seen_agents

def deselect_agents(seen_agents: List[AgentLike]):
  for previously_seen_agent in seen_agents:
    previously_seen_agent.deselect()
    render_deselected_agent(
      previously_seen_agent.identity.render_id, 
      previously_seen_agent.style.fill_color
    )

def find_other_agents(scene: Scene, agent_id: Tag) -> Dict[Tag, AgentLike]:
  other_agents: Dict[Tag, AgentLike] = {
    id: agent 
    for id, agent in scene.agents.items()
    if id != agent_id
  }
  return other_agents

@register_renderer(label='render_agents_with_labels')
def render_agents_with_labels(**data) -> None:
  context: SimulationContext = data['context']
  scene: Scene = context.scene
  agent: AgentLike

  for agent in scene.agents.values():
    agent_size: Size = agent.physicality.size
    agent_width_half: float = agent_size.width / 2.0
    agent_height_half: float = agent_size.height / 2.0

    with dpg.draw_node(tag=agent.identity.id):
      # Draw the triangle centered at cell (0,0) in the grid and pointing EAST.
      # The location of the triangle is transformed by update_all_agents_display()
      # which is called in the SimLoop.
      dpg.draw_triangle(
        tag       = agent.identity.render_id,
        p1        = (agent_width_half,0), 
        p2        = (-agent_width_half, -agent_height_half), 
        p3        = (-agent_width_half, agent_height_half), 
        color     = agent.style.stroke_color, 
        fill      = agent.style.fill_color, 
        thickness = agent.style.stroke_thickness
      )

      dpg.draw_text(
        pos   = (-5, -5), 
        text  = f'{agent.identity.id}',
        color = BasicColors.red.value,
        size  = DEFAULT_FONT_SIZE * 2
      )

@register_renderer(label='render_agents_view_frustum')
def render_agents_view_frustum(**data) -> None:
  context: SimulationContext = data['context']
  scene: Scene = context.scene

  agents: List[AgentLike] = list(
    filter(
      lambda agent: agent.identity.community_id != 1, 
      scene.agents.values()
    )
  )

  agent: AgentLike
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
      lambda agent: agent.identity.community_id == 1, 
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