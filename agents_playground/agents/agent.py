from collections.abc import Callable
from agents_playground.agents.direction import Direction, Vector2D
from agents_playground.agents.structures import Point
from agents_playground.renderers.color import Color, Colors
from agents_playground.simulation.tag import Tag

class Agent:
  """A generic, autonomous agent."""

  def __init__(self, 
    crest=Colors.red, 
    facing=Direction.EAST, 
    id: Tag=None, 
    render_id: Tag = None, 
    toml_id: Tag = None,
    location: Point=Point(0,0)) -> None:
    """Creates a new instance of an agent.
    
    Args:
      crest: The color to represent the agent.
      facing: The direction the agent is facing.
    """
    self._crest: Color = crest
    self._facing: Vector2D = facing
    self._location: Point = location # The coordinate of where the agent currently is.
    self._last_location: Point =  self._location # The last place the agent remembers it was.
    self._agent_scene_graph_changed = False
    self._agent_render_changed = False
    self._id: Tag = id # The ID used for the group node in the scene graph.
    self._render_id: Tag = render_id # The ID used for the triangle in the scene graph.
    self._toml_id:Tag = toml_id # The ID used in the TOML file.

  @property
  def id(self) -> Tag:
    return self._id

  @property
  def render_id(self) -> Tag:
    return self._render_id
    
  @property
  def crest(self) -> Color:
    return self._crest
  
  @crest.setter
  def crest(self, color: Color):
    self._agent_render_changed = True
    self._crest = color

  @property
  def facing(self) -> Vector2D:
    return self._facing

  @property
  def agent_scene_graph_changed(self) -> bool:
    return self._agent_scene_graph_changed

  @property
  def agent_render_changed(self) -> bool:
    return self._agent_render_changed

  def reset(self) -> None:
    self._agent_scene_graph_changed = False
    self._agent_render_changed = False

  def face(self, direction: Vector2D) -> None:
    """Set the direction the agent is facing."""
    self._facing = direction
    self._agent_scene_graph_changed = True

  def move_to(self, new_location: Point):
    """Tell the agent to walk to the new location in the maze."""
    self._last_location = self.location
    self._location = new_location
    self._agent_scene_graph_changed = True

  @property
  def location(self) -> Point:
    return self._location

  @property
  def last_location(self) -> Point:
    return self._last_location

  def movement_strategy(self, strategy: Callable[..., None]) -> None:
    """Assign a traversal algorithm to the agent."""
    self._movement_strategy = strategy

  # TODO: Define a better ADT for args. Keeping generic for now.
  def explore(self, **data) -> None:
    """Perform one step of the assigned traversal strategy."""
    self._movement_strategy(self, **data)
