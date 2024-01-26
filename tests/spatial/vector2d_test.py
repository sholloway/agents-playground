from math import radians
import math


from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vector.vector2d import Vector2d
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
    rotate_by = radians(90)
    east = Vector2d(1, 0)
    north = east.rotate(rotate_by)
    west = north.rotate(rotate_by)
    south = west.rotate(rotate_by)
    
    assert north == Vector2d(0, 1)
    assert west == Vector2d(-1, 0)
    assert south == Vector2d(0, -1)
    assert south.rotate(rotate_by) == east

  def test_length(self) -> None:
    assert Vector2d(2, 2).length()   == 2.8284271247461903
    assert Vector2d(2, -2).length()  == 2.8284271247461903
    assert Vector2d(-2, 2).length()  == 2.8284271247461903
    assert Vector2d(-2, -2).length() == 2.8284271247461903

  def test_unit(self) -> None:
    u = Vector2d(2,-8).unit()
    assert u == Vector2d(
      i = 0.24253562503633297,
      j = -0.9701425001453319
    )
    assert u.length() == 1
  
  def test_right_hand_perp(self) -> None:
    i = 7.2
    j = -3.1
    v = Vector2d(i, j)
    rp = v.right_hand_perp()
    assert rp == Vector2d(j, -i).unit() 
  
  def test_left_hand_perp(self) -> None:
    i = 7.2
    j = -3.1
    v = Vector2d(i, j)
    lp = v.left_hand_perp()
    assert lp == Vector2d(-j, i).unit()
  
  def test_project_onto(self) -> None:
    v = Vector2d(8, 2)
    o = Vector2d(17.2, 9.32)
    p = v.project_onto(o)
    assert p == Vector2d(
      i=7.0219784354631685,
      j=3.8049325010765545
    )
  
  def test_dot_product(self) -> None:
    # The angle between to vectors can be found with the dot product.
    # cos(theta) = (a dot b)/(len(a) * len(b))
    x_axis = Vector2d(1, 0)
    y_axis = Vector2d(0, 1)
    assert x_axis.dot(y_axis)/(x_axis.length() * y_axis.length()) == round(math.cos(radians(90)), 6)

  def test_cross_product(self) -> None:
    # The cross product between two vectors results in a vector that is perpendicular to the other two.
    # In 2D it is the right-handed perpendicular value of vector B
    x_axis = Vector2d(1, 0)
    y_axis = Vector2d(0, 1)
    assert x_axis.cross(y_axis) == y_axis.right_hand_perp()