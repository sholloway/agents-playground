from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vector2d import Vector2d
from agents_playground.spatial.vertex import Vertex2d


class TestVector2d:
  def test_from_vertices(self) -> None:
    v: Vector = Vector2d.from_vertices(Vertex2d(1,1), Vertex2d(4,2))
    assert v.i == -3 
    assert v.j == -1 
  
  def test_from_points(self) -> None:
    v: Vector = Vector2d.from_points(Coordinate(1,2), Coordinate(3,7))
    assert v.i == 2 
    assert v.j == 5 

  def test_scale_vector(self) -> None:
    v = Vector2d(4,1)
    vv = v.scale(3)
    assert vv.i == 12 
    assert vv.j == 3 
  
  def test_vector_to_point(self) -> None:
    point = Vector2d(4,-2).to_point(vector_origin=Coordinate(7,2))
    assert point.x == 11
    assert point.y == 0

  def test_vector_to_vertex(self) -> None:
    point = Vector2d(4,-2).to_vertex(vector_origin=Vertex2d(7,2))
    assert point.coordinates[0] == 11
    assert point.coordinates[1] == 0
  
  def test_rotate(self) -> None:
    assert False
  
  def test_unit(self) -> None:
    assert False
  
  def test_length(self) -> None:
    assert False
  
  def test_right_hand_perp(self) -> None:
    assert False
  
  def test_left_hand_perp(self) -> None:
    assert False
  
  def test_project_onto(self) -> None:
    assert False
  
  def test_dot_product(self) -> None:
    assert False
  
  def test_cross_product(self) -> None:
    assert False