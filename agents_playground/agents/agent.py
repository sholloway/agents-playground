from collections.abc import Callable
from enum import Enum
from typing import Any
from xmlrpc.client import Boolean

from numpy import format_float_scientific
from agents_playground.agents.direction import Direction, Vector2D
from agents_playground.core.types import Coordinate
from agents_playground.renderers.color import Color, Colors
from agents_playground.simulation.tag import Tag
from agents_playground.core.counter import Counter

class AgentState(Enum):
  IDLE: int = 0      # Not doing anything.
  RESTING: int = 0   # It is at a location, resting. 
  PLANNING: int = 2  # It is ready to travel and needs to select its next destination.
  ROUTING: int = 3   # It has selected a destination and needs to request from the Navigator to plan a route. 
  TRAVELING: int = 4 # It is traversing a route between two locations.

AgentStateMap = {
  AgentState.IDLE: AgentState.IDLE,
  AgentState.RESTING: AgentState.PLANNING,
  AgentState.PLANNING: AgentState.ROUTING,
  AgentState.ROUTING: AgentState.TRAVELING,
  AgentState.TRAVELING: AgentState.RESTING,
}

class Agent:
  """A generic, autonomous agent."""

  def __init__(self, 
    crest=Colors.red.value, 
    facing=Direction.EAST, 
    id: Tag=None, 
    render_id: Tag = None, 
    toml_id: Tag = None,
    location: Coordinate = Coordinate(0,0)) -> None:
    """Creates a new instance of an agent.
    
    Args:
      crest: The color to represent the agent.
      facing: The direction the agent is facing.
    """
    self.__crest: Color = crest
    self.__facing: Vector2D = facing
    self.__location: Coordinate = location # The coordinate of where the agent currently is.
    self.__last_location: Coordinate =  self.__location # The last place the agent remembers it was.
    self.__agent_scene_graph_changed = False
    self.__agent_render_changed = False
    self.__id: Tag = id # The ID used for the group node in the scene graph.
    self.__render_id: Tag = render_id # The ID used for the triangle in the scene graph.
    self.__toml_id:Tag = toml_id # The ID used in the TOML file.
    self.__state: AgentState = AgentState.IDLE
    self.__resting_counter: Counter = Counter(
      start=60, # The number of frames to rest.
      decrement_step=1, 
      min_value=0
    )
    self.__visible: Boolean = True
    self.__selected: Boolean = False

    # TODO Possibly move these fields somewhere else. They're used for the Our Town navigation.
    # Perhaps have a navigation object that bundles these.
    self.desired_location: Coordinate;
    self.active_route: Any; # Not using the real time of LinearPath due to circular reference between Agent and LinearPath.
    self.active_path_segment: int;
    self.walking_speed: float;
    self.active_t: float;

  @property 
  def visible(self) -> Boolean:
    return self.__visible

  @visible.setter
  def visible(self, is_visible: Boolean) -> None:
    self.__visible = is_visible
    self.__agent_render_changed = True

  # TODO: State will probably move elsewhere.
  @property
  def state(self) -> AgentState:
    return self.__state

  @state.setter
  def state(self, next_state) -> None:
    self.__state = next_state
  
  # TODO: The agent's resting counter will probably move elsewhere.
  @property
  def resting_counter(self) -> Counter:
    return self.__resting_counter

  @property
  def id(self) -> Tag:
    return self.__id

  @property
  def render_id(self) -> Tag:
    return self.__render_id

  @property
  def toml_id(self) -> Tag:
    return self.__toml_id
    
  @property
  def crest(self) -> Color:
    return self.__crest
  
  @crest.setter
  def crest(self, color: Color):
    self.__agent_render_changed = True
    self.__crest = color

  @property
  def facing(self) -> Vector2D:
    return self.__facing

  @property
  def agent_scene_graph_changed(self) -> bool:
    return self.__agent_scene_graph_changed

  @property
  def agent_render_changed(self) -> bool:
    return self.__agent_render_changed

  @property 
  def selected(self) -> Boolean:
    return self.__selected

  def select(self) -> None:
    self.__selected = True

  def deselect(self) -> None:
    self.__selected = False

  def reset(self) -> None:
    self.__agent_scene_graph_changed = False
    self.__agent_render_changed = False

  def face(self, direction: Vector2D) -> None:
    """Set the direction the agent is facing."""
    self.__facing = direction
    self.__agent_scene_graph_changed = True

  def move_to(self, new_location: Coordinate):
    """Tell the agent to walk to the new location in the maze."""
    self.__last_location = self.location
    self.__location = new_location
    self.__agent_scene_graph_changed = True

  @property
  def location(self) -> Coordinate:
    return self.__location

  @property
  def last_location(self) -> Coordinate:
    return self.__last_location

  def movement_strategy(self, strategy: Callable[..., None]) -> None:
    """Assign a traversal algorithm to the agent."""
    self._movement_strategy = strategy

  # TODO: Define a better ADT for args. Keeping generic for now.
  def explore(self, **data) -> None:
    """Perform one step of the assigned traversal strategy."""
    self._movement_strategy(self, **data)
