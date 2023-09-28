import pytest
from agents_playground.spatial.matrix import ( 
  MatrixError,
  MatrixOrder
)
from agents_playground.spatial.matrix4x4 import Matrix4x4, m4
from agents_playground.spatial.vector4d import Vector4d

class TestMatrix4x4:
  def test_initialization(self) -> None:
    m = m4(
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
    m = m4(
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
        except MatrixError:
          assert False, f'Calling Matrix.i should not have raised an exception for index ({i},{j}))'

    with pytest.raises(MatrixError):
      m.i(-1, 0)
    
    with pytest.raises(MatrixError):
      m.i(0, -1)
    
    with pytest.raises(MatrixError):
      m.i(-1, -1)
    
    with pytest.raises(MatrixError):
      m.i(4, 0)
    
    with pytest.raises(MatrixError):
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
    m = m4(
      1, 2, 3, 4,
      5, 6, 7, 8, 
      9, 10, 11, 12,
      13, 14, 15, 16
    )
    assert m.flatten(major=MatrixOrder.Row) == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
    assert m.flatten(major=MatrixOrder.Column) == (1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 4, 8, 12, 16)

  def test_transpose(self) -> None:
    m = m4(
      1, 2, 3, 4,
      5, 6, 7, 8, 
      9, 10, 11, 12,
      13, 14, 15, 16
    )
    assert m.transpose() == m4(*m.flatten(major=MatrixOrder.Column))

  def test_to_vectors(self) -> None:
    a = m4(
      1, 2, 3, 4,
      5, 6, 7, 8, 
      9, 10, 11, 12,
      13, 14, 15, 16 
    )
    assert a.to_vectors(MatrixOrder.Row) == (Vector4d(1, 2, 3, 4), Vector4d(5, 6, 7, 8), Vector4d(9, 10, 11, 12), Vector4d(13, 14, 15, 16))
    assert a.to_vectors(MatrixOrder.Column) == (Vector4d(1, 5, 9, 13), Vector4d(2, 6, 10, 14), Vector4d(3, 7, 11, 15), Vector4d(4, 8, 12, 16))

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

    c = a * b # type: ignore
    assert c == m4(
      210, 267, 236, 271,
      93, 149, 104, 149,
      171, 146, 172, 268,
      105, 169, 128, 169
    )

  def test_addition(self) -> None:
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

    c = a + b 
    assert c == m4(
      8, 17 , 21, 28,
      14, 4, 7, 17,
      17, 20, 14, 5,
      6, 15, 8, 18
    )
  
  def test_subtraction(self) -> None:
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

    c = a - b
    assert c == m4(
      2, -3, -3, -8,
      -10, 2, -1, -1,
      -1, 0, -10, 1,
      0, -9, 0, -2
    ) 
  
  def test_determinate(self) -> None:
    assert Matrix4x4.identity().det() == 1.0
    a = m4(
      1, 2, 3, 4,
      5, 6, 7, 8, 
      9, 10, 11, 12,
      13, 14, 15, 16
    )
    assert a.det() == 0

    b = m4(
      1, 1, 1, 0,
      0, 3, 1, 2,
      2, 3, 1, 0,
      1, 0, 2, 1
    )
    assert b.det() == -4

  def test_inverse(self) -> None:
    a = m4(
      1, 1, 1, 0,
      0, 3, 1, 2,
      2, 3, 1, 0,
      1, 0, 2, 1
    )

    assert a.inverse() == m4(
      -3, -0.5, 1.5, 1,
      1, 0.25, -0.25, -0.5,
      3, 0.25, -1.25, -0.5,
      -3, 0, 1, 1
    )

    i = Matrix4x4.identity()
    assert i.inverse() == Matrix4x4.identity()

    b = m4(
      1, 2, 3, 4,
      8, 9, 7, 8,
      9, 0, 1, 2,
      3, 4, 5, 6
    )
    assert b.det() == 60
    
    round_it = lambda i: round(i, 6)
    assert b.inverse().map(round_it) == m4(
      -0.2,     0,         0.1,  0.1,
      0.533333, 0.333333,  -0.1, -0.766667,
      -3.466667, -0.666667, -0.1, 3.233333,
      2.633333,  0.333333,  0.1,  -2.066667
    )
  

  def test_cannot_invert_matrix_with_no_determinate(self) -> None:
    m: Matrix4x4 = m4(
      1, 2, 3, 4,
      5, 6, 7, 8, 
      9, 10, 11, 12,
      13, 14, 15, 16
    )
    assert m.det() == 0
    with pytest.raises(MatrixError):
      m.inverse()