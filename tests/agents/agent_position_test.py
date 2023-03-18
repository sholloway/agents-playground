
from agents_playground.agents.default_agent import DefaultAgentPosition
from agents_playground.agents.direction import Vector2d
from agents_playground.core.types import Coordinate


class TestAgentPosition:
  def test_agent_position(self) -> None:
    agent_pos = DefaultAgentPosition(
      facing = Vector2d(1,0), 
      location = Coordinate(10,15),
      last_location = Coordinate(10, 14),
      desired_location = Coordinate(10, 15)
    )

    agent_pos.move_to(Coordinate(10,16))

    assert agent_pos.location == Coordinate(10,16)
    assert agent_pos.last_location == Coordinate(10,15)