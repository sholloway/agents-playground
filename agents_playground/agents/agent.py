from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from agents_playground.agents.direction import Vector2d
from agents_playground.core.types import AABBox, Coordinate, EmptyAABBox, Size
from agents_playground.simulation.tag import Tag
from agents_playground.counter.counter import Counter
from agents_playground.styles.agent_style import AgentStyle

class AgentActionState(Enum):
  IDLE: int       = 0 # Not doing anything.
  RESTING: int    = 1 # It is at a location, resting. 
  PLANNING: int   = 2 # It is ready to travel and needs to select its next destination.
  ROUTING: int    = 3 # It has selected a destination and needs to request from the Navigator to plan a route. 
  TRAVELING: int  = 4 # It is traversing a route between two locations.


AgentStateMap = {
  AgentActionState.IDLE: AgentActionState.IDLE,
  AgentActionState.RESTING: AgentActionState.PLANNING,
  AgentActionState.PLANNING: AgentActionState.ROUTING,
  AgentActionState.ROUTING: AgentActionState.TRAVELING,
  AgentActionState.TRAVELING: AgentActionState.RESTING,
}

@dataclass
class ActionSelector:
  model: Dict[AgentActionState, AgentActionState]

  # TODO: Eventually, this will be probabilistic.
  def next_action(self, current_action: AgentActionState) -> AgentActionState:
    """Find the mapped next action."""
    return self.model[current_action]

  def __repr__(self) -> str:
    """An implementation of the dunder __repr__ method. Used for debugging."""
    model_rep = ''
    for k,v in self.model.items():
      model_rep = model_rep + f'{k} -> {v}\n'

    return f'{self.__class__.__name__}\n{model_rep}' 

def create_agent_selector() -> ActionSelector:
  return ActionSelector(model = AgentStateMap)

@dataclass
class AgentState:
  current_action_state: AgentActionState      = field(default = AgentActionState.IDLE)
  last_action_state: AgentActionState | None  = field(default = None)
  action_selector: ActionSelector             = field(default_factory = create_agent_selector)
  selected: bool                           = field(default = False)
  require_scene_graph_update: bool         = field(default = False)
  require_render: bool                     = field(default = False)
  visible: bool                            = field(default = True)

  def reset(self) -> None:
    self.require_scene_graph_update = False
    self.require_render = False

  def transition_to_next_action(self) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = self.action_selector.next_action(self.current_action_state)

  def assign_action_state(self, next_state: AgentActionState) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = next_state

  def set_visibility(self, is_visible: bool) -> None:
    self.visible = is_visible
    self.require_render = True

@dataclass
class AgentIdentity:
  id: Tag         # The ID used for the group node in the scene graph.
  toml_id: Tag    # The ID used in the TOML file.
  render_id: Tag  # The ID used for the triangle in the scene graph.
  aabb_id: Tag    # The ID used rendering the agent's AABB.

  def __init__(self, id_generator: Callable) -> None:
    self.id         = id_generator()
    self.render_id  = id_generator()
    self.toml_id    = id_generator()
    self.aabb_id    = id_generator()

@dataclass
class AgentPhysicality:
  size: Size 
  aabb: AABBox 

  def __init__(self, size: Size) -> None:
    self.size = size
    self.aabb = EmptyAABBox()

  def calculate_aabb(self, agent_location: Coordinate, cell_size: Size) -> None:
    agent_half_width:float  = self.size.width  / 2.0
    agent_half_height:float = self.size.height / 2.0
    cell_half_width         = cell_size.width  / 2.0
    cell_half_height        = cell_size.height / 2.0

    # 1. Convert the agent's location to a canvas space.
    # agent_loc: Coordinate = cell_to_canvas(agent.location, cell_size)
    agent_loc: Coordinate = agent_location.multiply(Coordinate(cell_size.width, cell_size.height))

    # 2. Agent's are shifted to be drawn in near the center of a grid cell, 
    # the AABB needs to be shifted as well.
    agent_loc = agent_loc.shift(Coordinate(cell_half_width, cell_half_height))

    # 3. Create an AABB for the agent with the agent's location at its centroid.
    min_coord = Coordinate(agent_loc.x - agent_half_width, agent_loc.y - agent_half_height)
    max_coord = Coordinate(agent_loc.x + agent_half_width, agent_loc.y + agent_half_height)
    self.aabb = AABBox(min_coord, max_coord)

@dataclass
class AgentPosition:
  facing: Vector2d
  location: Coordinate          # The coordinate of where the agent currently is.
  last_location: Coordinate     # The last place the agent remembers it was.
  desired_location: Coordinate  # Where the agent wants to go next.

  def move_to(self, new_location: Coordinate):
    """Tell the agent to walk to the new location in the maze."""
    self.last_location = self.location
    self.location = new_location

# TODO: Move into a dedicated file and change active_route's type from 
# Any to InterpolatedPath.
@dataclass
class AgentMovement:
  resting_counter: Counter 

  # These attributes are initialized be the relevant movement task when needed.
  active_route: Any # Not using the real type of LinearPath due to circular reference between Agent and LinearPath.
  active_path_segment: int
  walking_speed: float
  active_t: float

  def __init__(self) -> None:
    # If an agent is resting, this counts the number of frames to rest for.
    self.resting_counter = Counter(
      start=60, # The number of frames to rest.
      decrement_step=1, 
      min_value=0
    )

class Agent:
  """A generic, autonomous agent."""

  def __init__(
    self, 
    initial_state: AgentState, 
    style: AgentStyle,
    identity: AgentIdentity,
    physicality: AgentPhysicality,
    position: AgentPosition,
    movement: AgentMovement
  ) -> None:
    """Creates a new instance of an agent.
    
    Args:
      initial_state - The initial configuration for the various state fields.
      style - Define's the agent's look.
      identity - All of the agent's IDs.
      physicality - The agent's physical attributes.
      position - All the attributes related to where the agent is.
      movement - Attributes used for movement.
    """
    
    self._state: AgentState             = initial_state
    self._style: AgentStyle             = style
    self._identity: AgentIdentity       = identity
    self._physicality: AgentPhysicality = physicality
    self._position: AgentPosition       = position
    self._movement: AgentMovement       = movement
  
  def transition_state(self) -> None:
    self._state.transition_to_next_action()

  @property
  def style(self) -> AgentStyle:
    return self._style

  @property
  def state(self) -> AgentState:
    return self._state

  @property
  def identity(self) -> AgentIdentity:
    return self._identity

  @property
  def physicality(self) -> AgentPhysicality:
    return self._physicality
  
  @property
  def position(self) -> AgentPosition:
    return self._position
  
  @property
  def movement(self) -> AgentMovement:
    return self._movement

  @property
  def agent_scene_graph_changed(self) -> bool:
    return self._state.require_scene_graph_update

  @property
  def agent_render_changed(self) -> bool:
    return self._state.require_render

  @property 
  def selected(self) -> bool:
    return self._state.selected

  def select(self) -> None:
    self._state.selected = True

  def deselect(self) -> None:
    self._state.selected = False

  def reset(self) -> None:
    self._state.reset()

  def face(self, direction: Vector2d) -> None:
    """Set the direction the agent is facing."""
    self._position.facing = direction
    self._state.require_scene_graph_update = True

  def move_to(self, new_location: Coordinate, cell_size: Size):
    """Tell the agent to walk to the new location in the maze."""
    self._position.move_to(new_location)
    self._state.require_scene_graph_update= True
    self._physicality.calculate_aabb(self._position.location, cell_size)