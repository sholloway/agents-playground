from pytest_mock import MockFixture
from agents_playground.core.types import Size
from agents_playground.spatial.aabbox import AABBox, AABBox2d

from agents_playground.spatial.frustum import Frustum, Frustum2d
from agents_playground.spatial.polygon import Polygon
from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vector2d import Vector2d
from agents_playground.spatial.vertex import Vertex2d

class TestFrustum2d:
  def test_update(self) -> None:
    frustum: Frustum = Frustum2d()
    frustum.update(
      grid_location = Coordinate(x=36, y=18),
      direction     = Vector2d(i=1,j=0), 
      cell_size     = Size(w=20, h=20)
    )

    assert frustum.vertices[0].coordinates == (738.6602540378444, 355.0)
    assert frustum.vertices[1].coordinates == (738.6602540378444, 385.0)
    assert frustum.vertices[2].coordinates == (1163.0127018922194, 1119.9999999999995)
    assert frustum.vertices[3].coordinates == (1163.0127018922194, -379.99999999999966)

  def test_intersect(self) -> None:
    aabb: Polygon = AABBox2d(center = Vertex2d(0,0), half_height=20, half_width=20)
    frustum: Frustum = Frustum2d()
    overlapping = frustum.intersect(aabb)
    assert overlapping, "Expected the AABB and frustum to be overlapping."