from pytest_mock import MockFixture
from agents_playground.core.types import Size
from agents_playground.spatial.aabbox import AABBox

from agents_playground.spatial.frustum import Frustum, Frustum2d
from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vector2d import Vector2d

class TestFrustum2d:
  def test_update(self) -> None:
    frustum: Frustum = Frustum2d()
    frustum.update(
      grid_location = Coordinate(x=36, y=18),
      direction     = Vector2d(i=1,j=0), 
      cell_size     = Size(w=20, h=20)
    )

    assert frustum.p1 == Coordinate(738.6602540378444, 385.0)
    assert frustum.p2 == Coordinate(1163.0127018922194, 1119.9999999999995)
    assert frustum.p3 == Coordinate(1163.0127018922194, -379.99999999999966)
    assert frustum.p4 == Coordinate(738.6602540378444, 355.0)

  def test_intersect(self) -> None:
    aabb: Polygon = AABBox()
    frustum: Frustum = Frustum2d()
    overlaping = frustum.intersect(aabb)
    assert overlaping, "Expected the AABB and frustum to be overlapping."