from collections.abc import Callable
from agents_playground.agents.direction import Direction
from agents_playground.agents.structures import Point

class Agent:
  """A generic, autonomous agent."""

  def __init__(self, crest='blue', facing=Direction.EAST) -> None:
    """Creates a new instance of an agent.
    
    Args:
      crest: The color to represent the agent.
      facing: The direction the agent is facing.
    """
    self._crest: str = crest
    self._facing: Direction = facing
    self._location: Point = Point(0,0) # The coordinate of where the agent currently is.
    self._last_location: Point = Point(0,0) # The last place the agent remembers it was.
    self._agent_changed = False


  @property
  def crest(self) -> str:
    return self._crest

  @property
  def facing(self) -> Direction:
    return self._facing

  @property
  def agent_changed(self) -> bool:
    return self._agent_changed

  def reset(self) -> None:
    self._agent_changed = False

  def face(self, direction: Direction) -> None:
    """Set the direction the agent is facing."""
    self._facing = direction
    self._agent_changed = True

  def move_to(self, new_location: Point):
    """Tell the agent to walk to the new location in the maze."""
    self._last_location = self.location
    self._location = new_location
    self._agent_changed = True

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
