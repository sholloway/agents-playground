import pytest

from math import cos, radians, sin

from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4, m4
from agents_playground.spatial.vector import vector
from agents_playground.spatial.matrix.transformation import Transformation

@pytest.fixture
def t() -> Transformation:
  """A test fixture that returns an empty transformation"""
  return Transformation()

class TestTransformation:
  def test_empty_transformation(self, t: Transformation) -> None:
    assert t.transform() == Matrix4x4.identity()

  def test_transformation(self, t: Transformation) -> None:
    a = m4(
      5, 7, 9, 10,
      2, 3, 3, 8,
      8, 10, 2, 3,
      3, 3, 4, 8
    )

    b = m4(
      3, 10, 12, 18,
      12, 1, 4, 9,
      9, 10, 12, 2,
      3, 12, 4, 10
    )
    
    t.identity().mul(a).mul(b)

    # Multiply Identity * Matrix A * Matrix B
    transformation_matrix = t.transform()

    assert transformation_matrix == m4(
      210, 267, 236, 271,
      93, 149, 104, 149,
      171, 146, 172, 268,
      105, 169, 128, 169
    )

  def test_translation(self, t: Transformation) -> None:
    t.translate(vector(4, 5, 6))
    assert t.transform() == m4(
      1, 0, 0, 4,
      0, 1, 0, 5,
      0, 0, 1, 6,
      0, 0, 0, 1
    )

  def test_rotate_around_x_axis(self, t: Transformation) -> None:
    angle = 90 # In degrees.
    rads = radians(angle)
    c = cos(rads)
    s = sin(rads)
    
    t.rotate_around_x(angle)

    assert t.transform() == m4(
      1, 0, 0, 0,
      0, c, -s, 0,
      0, s, c, 0,
      0, 0, 0, 1
    )
  
  def test_rotate_around_y_axis(self, t: Transformation) -> None:
    angle = 72 # In degrees.
    rads = radians(angle)
    c = cos(rads)
    s = sin(rads)

    t.rotate_around_y(angle)

    assert t.transform() == m4(
      c, 0, s, 0,
      0, 1, 0, 0,
      -s, 0, c, 0,
      0, 0, 0, 1
    )
  
  def test_rotate_around_z_axis(self, t: Transformation) -> None:
    angle = 19 # In degrees.
    rads = radians(angle)
    c = cos(rads)
    s = sin(rads)

    t.rotate_around_z(angle)

    assert t.transform() == m4(
      c, -s, 0, 0,
      s, c, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1
    )