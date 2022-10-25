from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict
from xmlrpc.client import Boolean

from numpy import format_float_scientific
from agents_playground.agents.direction import Direction, Vector2d
from agents_playground.core.types import AABBox, Coordinate, Size
from agents_playground.renderers.color import Color, Colors
from agents_playground.simulation.tag import Tag
from agents_playground.core.counter import Counter
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

class ActionSelector:
  def __init__(self, model: Dict[AgentActionState, AgentActionState]) -> None:
    self._model = model

  # TODO: Eventually, this will be probabilistic.
  def next_action(self, current_action: AgentActionState) -> AgentActionState:
    """Find the mapped next action."""
    return self._model[current_action]

@dataclass
class AgentState:
  current_action_state: AgentActionState      = field(default = AgentActionState.IDLE)
  last_action_state: AgentActionState | None  = field(default = None)
  action_selector: ActionSelector             = field(default = ActionSelector(model = AgentStateMap))
  selected: Boolean                           = field(default = False)
  require_scene_graph_update: Boolean         = field(default = False)
  require_render: Boolean                     = field(default = False)
  visible: Boolean                            = field(default = True)

  def reset(self) -> None:
    self.require_scene_graph_update = False
    self.require_render = False

  def transition_to_next_action(self) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = self.action_selector.next_action(self.current_action_state)

  def assign_action_state(self, next_state: AgentActionState) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = next_state

  def set_visibility(self, is_visible: Boolean) -> None:
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

class EmptyAABBox(AABBox):
  def __init__(self) -> None:
    super().__init__(Coordinate(0,0), Coordinate(0,0))

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

class Agent:
  """A generic, autonomous agent."""

  def __init__(
    self, 
    initial_state: AgentState, 
    style: AgentStyle,
    identity: AgentIdentity,
    physicality: AgentPhysicality,
    position: AgentPosition
  ) -> None:
    """Creates a new instance of an agent.
    
    Args:
      crest: The color to represent the agent.
      facing: The direction the agent is facing.
    """
    
    self._state: AgentState = initial_state
    self._style: AgentStyle = style
    self._identity: AgentIdentity = identity
    self._physicality: AgentPhysicality = physicality
    self._position: AgentPosition = position
   
    # Movement related...
    # TODO Move these fields somewhere else. They're used for the Our Town navigation.
    # Perhaps have a navigation object that bundles these.
    self._resting_counter: Counter = Counter(
      start=60, # The number of frames to rest.
      decrement_step=1, 
      min_value=0
    )
    self.active_route: Any; # Not using the real time of LinearPath due to circular reference between Agent and LinearPath.
    self.active_path_segment: int;
    self.walking_speed: float;
    self.active_t: float;

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
  
  # TODO: The agent's resting counter will probably move elsewhere.
  @property
  def resting_counter(self) -> Counter:
    return self._resting_counter

  @property
  def agent_scene_graph_changed(self) -> bool:
    return self._state.require_scene_graph_update

  @property
  def agent_render_changed(self) -> bool:
    return self._state.require_render

  @property 
  def selected(self) -> Boolean:
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

  def movement_strategy(self, strategy: Callable[..., None]) -> None:
    """Assign a traversal algorithm to the agent."""
    self._movement_strategy = strategy

  # TODO: Define a better ADT for args. Keeping generic for now.
  def explore(self, **data) -> None:
    """Perform one step of the assigned traversal strategy."""
    self._movement_strategy(self, **data)
