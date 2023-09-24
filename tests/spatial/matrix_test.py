import pytest
from agents_playground.spatial.matrix import (
  m4,
  Matrix4x4, 
  Matrix4x4Error,
  MatrixOrder
)
from agents_playground.spatial.vector4d import Vector4d

class TestMatrix4x4:
  def test_initialization(self) -> None:
    m: Matrix4x4 = m4(
      1, 2, 3, 4,
      5, 6, 7, 8, 
      9, 10, 11, 12,
      13, 14, 15, 16
    )
    n = Matrix4x4((
      (1, 2, 3, 4),
      (5, 6, 7, 8),
      (9, 10, 11, 12),
      (13, 14, 15, 16)
    ))
    assert m == n
    
  def test_at_index(self) -> None:
    m: Matrix4x4 = m4(
      1, 2, 3, 4,
      5, 6, 7, 8, 
      9, 10, 11, 12,
      13, 14, 15, 16
    )
    
    expected_value = 1
    for i in range(4):
      for j in range(4):
        assert m.i(i, j) == expected_value
        expected_value += 1

  def test_fill(self) -> None:
    assert Matrix4x4.fill(1) == m4(
      1, 1, 1, 1,
      1, 1, 1, 1,
      1, 1, 1, 1,
      1, 1, 1, 1
    )
    
    assert Matrix4x4.fill(3.14) == m4(
      3.14, 3.14, 3.14, 3.14,
      3.14, 3.14, 3.14, 3.14,
      3.14, 3.14, 3.14, 3.14,
      3.14, 3.14, 3.14, 3.14
    )

  def test_invalid_index(self) -> None:
    m = Matrix4x4.fill(1)
    for i in range(4):
      for j in range(4):
        try:
          m.i(i,j)
        except Matrix4x4Error:
          assert False, f'Calling Matrix.i should not have raised an exception for index ({i},{j}))'

    with pytest.raises(Matrix4x4Error):
      m.i(-1, 0)
    
    with pytest.raises(Matrix4x4Error):
      m.i(0, -1)
    
    with pytest.raises(Matrix4x4Error):
      m.i(-1, -1)
    
    with pytest.raises(Matrix4x4Error):
      m.i(4, 0)
    
    with pytest.raises(Matrix4x4Error):
      m.i(0, 4)

  def test_identity(self) -> None:
    i = Matrix4x4.identity()
    assert i == m4(
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1
    )

  def test_flatten(self) -> None:
    m: Matrix4x4 = m4(
      1, 2, 3, 4,
      5, 6, 7, 8, 
      9, 10, 11, 12,
      13, 14, 15, 16
    )
    assert m.flatten(major=MatrixOrder.Row) == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
    assert m.flatten(major=MatrixOrder.Column) == (1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16)

  def test_transpose(self) -> None:
    m: Matrix4x4 = m4(
      1, 2, 3, 4,
      5, 6, 7, 8, 
      9, 10, 11, 12,
      13, 14, 15, 16
    )
    assert m.transpose() == m4(*m.flatten(major=MatrixOrder.Column))

  def test_multiplication(self) -> None:
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

    c = a * b
    assert c == m4(
      210, 267, 236, 271,
      93, 149, 104, 149,
      171, 146, 172, 268,
      105, 169, 128, 169
    )