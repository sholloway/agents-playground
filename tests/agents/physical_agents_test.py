
from agents_playground.agents.default.default_agent_physicality import DefaultAgentPhysicality
from agents_playground.core.types import Size
from agents_playground.spatial.aabbox import EmptyAABBox
from agents_playground.spatial.frustum import Frustum2d
from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vertex import Vertex2d

class TestPhysicalAgents:
  def test_aabb(self) -> None:
    physicality = DefaultAgentPhysicality(
      size = Size(12, 6),
      aabb = EmptyAABBox(),
      frustum = Frustum2d.create_empty()
    )
    assert physicality.aabb.min.coordinates == Vertex2d(0,0).coordinates
    assert physicality.aabb.max.coordinates == Vertex2d(0,0).coordinates

    physicality.calculate_aabb(
      agent_location = Coordinate(0,0),
      cell_size      = Size(10, 10)
    )
    
    assert physicality.aabb.min.coordinates == Vertex2d(-1, 2).coordinates
    assert physicality.aabb.max.coordinates == Vertex2d(11, 8).coordinates