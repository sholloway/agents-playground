
from agents_playground.agents.default.default_agent_physicality import DefaultAgentPhysicality
from agents_playground.core.types import Size
from agents_playground.spatial.types import Coordinate

class TestPhysicalAgents:
  def test_aabb(self) -> None:
    physicality = DefaultAgentPhysicality(size = Size(12, 6))
    assert physicality.aabb.min == Coordinate(0,0)
    assert physicality.aabb.max == Coordinate(0,0)

    physicality.calculate_aabb(
      agent_location = Coordinate(0,0),
      cell_size      = Size(10, 10)
    )
    
    assert physicality.aabb.min == Coordinate(-1, 2)
    assert physicality.aabb.max == Coordinate(11, 8)