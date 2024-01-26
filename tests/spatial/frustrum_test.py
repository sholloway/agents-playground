from pytest_mock import MockFixture
from agents_playground.core.types import Size
from agents_playground.spatial.aabbox import AABBox, AABBox2d

from agents_playground.spatial.frustum import Frustum, Frustum2d
from agents_playground.spatial.polygon import Polygon
from agents_playground.spatial.coordinate import Coordinate
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
    round_it = lambda i: round(i, 1)
    assert tuple(map(round_it, frustum.vertices[0].coordinates)) == (738.7, 355.0)
    assert tuple(map(round_it, frustum.vertices[1].coordinates)) == (738.7, 385.0)
    assert tuple(map(round_it, frustum.vertices[2].coordinates)) == (1163.0, 1120.0)
    assert tuple(map(round_it, frustum.vertices[3].coordinates)) == (1163.0, -380.0)

  def test_intersect_aabb(self) -> None:
    """
    Place a frustum at (50,50). Have an aabb to the N/W/S/E of it.
    Rotate the frustum and check which boxes are intersecting the frustum.
    """
    south_aabb: Polygon = AABBox2d(center = Vertex2d(50,1),  half_height=2, half_width=2)
    west_aabb: Polygon  = AABBox2d(center = Vertex2d(1,50), half_height=2, half_width=2)
    north_aabb: Polygon = AABBox2d(center = Vertex2d(50,100), half_height=2, half_width=2)
    east_aabb: Polygon  = AABBox2d(center = Vertex2d(100,50), half_height=2, half_width=2)

    # at (50,50)
    frustum: Frustum = Frustum2d(near_plane_depth = 10, depth_of_field = 100, field_of_view = 120)

    cell_size = Size(1,1) # set the cell size to 1,1 so the math is easier.
    frustum_location = Coordinate(50,50)
    north = Vector2d(0,1)
    south = Vector2d(0,-1)
    east = Vector2d(1,0)
    west = Vector2d(-1,0)
    
    frustum.update(frustum_location, direction=north, cell_size = cell_size)
    
    # Direction:    N | S | E | W
    # Intersection: 1 | 0 | 0 | 0
    assert frustum.intersect(north_aabb)
    assert not frustum.intersect(west_aabb)
    assert not frustum.intersect(south_aabb)
    assert not frustum.intersect(east_aabb)
    
    
    frustum.update(frustum_location, direction=south, cell_size = cell_size)
    
    # Direction:    N | S | E | W
    # Intersection: 0 | 1 | 0 | 0
    assert not frustum.intersect(north_aabb)
    assert not frustum.intersect(west_aabb)
    assert frustum.intersect(south_aabb)
    assert not frustum.intersect(east_aabb)
    
    frustum.update(frustum_location, direction=east, cell_size = cell_size)
    
    # Direction:    N | S | E | W
    # Intersection: 0 | 0 | 1 | 0
    assert not frustum.intersect(north_aabb)
    assert not frustum.intersect(west_aabb)
    assert not frustum.intersect(south_aabb)
    assert frustum.intersect(east_aabb)
    
    frustum.update(frustum_location, direction=west, cell_size = cell_size)
    
    # Direction:    N | S | E | W
    # Intersection: 0 | 0 | 0 | 1
    assert not frustum.intersect(north_aabb)
    assert frustum.intersect(west_aabb)
    assert not frustum.intersect(south_aabb)
    assert not frustum.intersect(east_aabb)