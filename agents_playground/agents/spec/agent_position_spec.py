from abc import abstractmethod
from typing import Protocol
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vector import Vector

from agents_playground.spatial.vector2d import Vector2d

class AgentPositionLike(Protocol):
  facing: Vector              # The direction the agent is facing.
  location: Coordinate          # The coordinate of where the agent currently is.
  last_location: Coordinate     # The last place the agent remembers it was.
  desired_location: Coordinate  # Where the agent wants to go next.

  @abstractmethod
  def move_to(self, new_location: Coordinate):
    """Moves the agent to to a new location."""
    ...