from abc import abstractmethod
from typing import Protocol

from agents_playground.agents.direction import Vector2d
from agents_playground.core.types import Coordinate


class AgentPositionLike(Protocol):
  facing: Vector2d              # The direction the agent is facing.
  location: Coordinate          # The coordinate of where the agent currently is.
  last_location: Coordinate     # The last place the agent remembers it was.
  desired_location: Coordinate  # Where the agent wants to go next.

  @abstractmethod
  def move_to(self, new_location: Coordinate):
    """Moves the agent to to a new location."""
    ...