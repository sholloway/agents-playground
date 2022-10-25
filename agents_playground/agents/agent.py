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

  def reset(self) -> None:
    self.require_scene_graph_update = False
    self.require_render = False

  def transition_to_next_action(self) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = self.action_selector.next_action(self.current_action_state)

  def assign_action_state(self, next_state: AgentActionState) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = next_state

class EmptyAABBox(AABBox):
  def __init__(self) -> None:
    super().__init__(Coordinate(0,0), Coordinate(0,0))

class Agent:
  """A generic, autonomous agent."""

  def __init__(
    self, 
    initial_state: AgentState, 
    style: AgentStyle,
    facing=Direction.EAST, 
    id: Tag=None, 
    render_id: Tag = None, 
    toml_id: Tag = None,
    aabb_id: Tag = None,
    location: Coordinate = Coordinate(0,0)) -> None:
    """Creates a new instance of an agent.
    
    Args:
      crest: The color to represent the agent.
      facing: The direction the agent is facing.
    """
    
    self._state: AgentState = initial_state
    self._style: AgentStyle = style
    self._facing: Vector2d = facing
    self._location: Coordinate = location # The coordinate of where the agent currently is.
    self._last_location: Coordinate =  self._location # The last place the agent remembers it was.
    self._id: Tag = id # The ID used for the group node in the scene graph.
    self._render_id: Tag = render_id # The ID used for the triangle in the scene graph.
    self._toml_id:Tag = toml_id # The ID used in the TOML file.
    self._aabb_id: Tag = aabb_id # The ID used rendering the agent's AABB.
   
    self._resting_counter: Counter = Counter(
      start=60, # The number of frames to rest.
      decrement_step=1, 
      min_value=0
    )
    self._visible: Boolean = True
    
    self._aabb: AABBox = EmptyAABBox()

    # TODO Move these fields somewhere else. They're used for the Our Town navigation.
    # Perhaps have a navigation object that bundles these.
    self.desired_location: Coordinate;
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
  def bounding_box(self) -> AABBox:
    """Returns the axis-aligned bounding box of the agent."""
    return self._aabb

  @property 
  def visible(self) -> Boolean:
    return self._visible

  @visible.setter
  def visible(self, is_visible: Boolean) -> None:
    self._visible = is_visible
    self._state.require_render = True
  
  # TODO: The agent's resting counter will probably move elsewhere.
  @property
  def resting_counter(self) -> Counter:
    return self._resting_counter

  @property
  def id(self) -> Tag:
    return self._id

  @property
  def render_id(self) -> Tag:
    return self._render_id

  @property
  def toml_id(self) -> Tag:
    return self._toml_id

  @property
  def aabb_id(self) -> Tag:
    return self._aabb_id

  @property
  def facing(self) -> Vector2d:
    return self._facing

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
    self._facing = direction
    self._state.require_scene_graph_update = True

  def move_to(self, new_location: Coordinate, cell_size: Size):
    """Tell the agent to walk to the new location in the maze."""
    self._last_location = self.location
    self._location = new_location
    self._state.require_scene_graph_update= True
    self._calculate_aabb(self._style.size, cell_size)

  def _calculate_aabb(self, agent_size: Size, cell_size: Size) -> None:
    agent_half_width:float  = agent_size.width / 2.0
    agent_half_height:float = agent_size.height / 2.0
    cell_half_width         = cell_size.width / 2.0
    cell_half_height        = cell_size.height / 2.0

    # 1. Convert the agent's location to a canvas space.
    # agent_loc: Coordinate = cell_to_canvas(agent.location, cell_size)
    agent_loc: Coordinate = self._location.multiply(Coordinate(cell_size.width, cell_size.height))

    # 2. Agent's are shifted to be drawn in near the center of a grid cell, 
    # the AABB needs to be shifted as well.
    agent_loc = agent_loc.shift(Coordinate(cell_half_width, cell_half_height))

    # 3. Create an AABB for the agent with the agent's location at its centroid.
    min_coord = Coordinate(agent_loc.x - agent_half_width, agent_loc.y - agent_half_height)
    max_coord = Coordinate(agent_loc.x + agent_half_width, agent_loc.y + agent_half_height)
    self._aabb = AABBox(min_coord, max_coord)

  @property
  def location(self) -> Coordinate:
    return self._location

  @property
  def last_location(self) -> Coordinate:
    return self._last_location

  def movement_strategy(self, strategy: Callable[..., None]) -> None:
    """Assign a traversal algorithm to the agent."""
    self._movement_strategy = strategy

  # TODO: Define a better ADT for args. Keeping generic for now.
  def explore(self, **data) -> None:
    """Perform one step of the assigned traversal strategy."""
    self._movement_strategy(self, **data)
