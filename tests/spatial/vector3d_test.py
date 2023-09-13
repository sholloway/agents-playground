from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vector3d import Vector3d
from agents_playground.spatial.vertex import Vertex3d

class TestVector3d:
  def test_from_vertices(self) -> None:
    v: Vector = Vector3d.from_vertices(Vertex3d(1, 2, 3), Vertex3d(4, 5, 6))
    assert v.i == -3 
    assert v.j == -3 
    assert v.k == -3 
  
  def test_scale_vector(self) -> None:
    v = Vector3d(1, 2, 3)
    vv = v.scale(3)
    assert vv.i == 3
    assert vv.j == 6
    assert vv.k == 9
  
  def test_vector_to_vertex(self) -> None:
    assert False
  
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