
from agents_playground.agents.spec.agent_position_spec import AgentPositionLike
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vector.vector2d import Vector2d

class DefaultAgentPosition(AgentPositionLike):
  def __init__(
    self, 
    facing: Vector2d, 
    location: Coordinate, 
    last_location: Coordinate, 
    desired_location: Coordinate
  ) -> None:
    self.facing           = facing
    self.location         = location
    self.last_location    = last_location
    self.desired_location = desired_location

  def move_to(self, new_location: Coordinate) -> None:
    self.last_location = self.location
    self.location = new_location