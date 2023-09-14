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
    vertex = Vector3d(4,-2, 3).to_vertex(vector_origin=Vertex3d(7,2,5))
    assert vertex.coordinates[0] == 11
    assert vertex.coordinates[1] == 0
    assert vertex.coordinates[2] == 8
  
  def test_rotate(self) -> None:
    assert False
  
  def test_unit(self) -> None:
    assert Vector3d(7, -2, 17.3).unit() == Vector3d(
      i = 0.3729476562455045,
      j = -0.10655647321300128, 
      k = 0.9217134932924611
    )
  
  def test_length(self) -> None:
    assert Vector3d(2, 2, 2).length()    == 3.4641016151377544
    assert Vector3d(-2, 2, 2).length()   == 3.4641016151377544
    assert Vector3d(2, -2, 2).length()   == 3.4641016151377544
    assert Vector3d(2, 2, -2).length()   == 3.4641016151377544
    assert Vector3d(-2, -2, -2).length() == 3.4641016151377544
  
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