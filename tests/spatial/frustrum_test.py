from pytest_mock import MockFixture
from agents_playground.core.types import Size

from agents_playground.spatial.frustum import Frustum, Frustum2d
from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vector2d import Vector2d

class TestFrustum2d:
  def test_shit(self) -> None:
    frustum: Frustum = Frustum2d()
    frustum.update(
      grid_location = Coordinate(x=36, y=18),
      direction     = Vector2d(i=1,j=0), 
      cell_size     = Size(w=20, h=20)
    )

    assert frustum.t1 == Coordinate(x=730.0, y=370.0)
    assert frustum.t2 == Coordinate(x=773.3012701892219, y=445.0)
    assert frustum.t3 == Coordinate(x=773.3012701892219, y=295.0)