
import pytest
from agents_playground.spatial.matrix import MatrixError, MatrixOrder
from agents_playground.spatial.matrix3x3 import Matrix3x3, m3


class TestMatrix3x3:
  def test_initialization(self) -> None:
    m: Matrix3x3 = m3(
      1, 2, 3, 
      5, 6, 7, 
      9, 10, 11
    )
    n = Matrix3x3((
      (1, 2, 3),
      (5, 6, 7),
      (9, 10, 11)
    ))
    assert m == n

  def test_at_index(self) -> None:
    m: Matrix3x3 = m3(
      1, 2, 3, 
      4, 5, 6,
      7, 8, 9
    )
    
    expected_value = 1
    for i in range(3):
      for j in range(3):
        assert m.i(i, j) == expected_value
        expected_value += 1

  def test_fill(self) -> None:
    assert Matrix3x3.fill(1) == m3(
      1, 1, 1,
      1, 1, 1,
      1, 1, 1
    )
    
    assert Matrix3x3.fill(3.14) == m3(
      3.14, 3.14, 3.14,
      3.14, 3.14, 3.14,
      3.14, 3.14, 3.14
    )

  def test_invalid_index(self) -> None:
    m = Matrix3x3.fill(1)
    for i in range(3):
      for j in range(3):
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
      m.i(3, 0)
    
    with pytest.raises(MatrixError):
      m.i(0, 3)

  def test_identity(self) -> None:
    i = Matrix3x3.identity()
    assert i == m3(
      1, 0, 0,
      0, 1, 0,
      0, 0, 1
    )

  def test_flatten(self) -> None:
    m: Matrix3x3 = m3(
      1, 2, 3, 
      4, 5, 6, 
      7, 8, 9
    )
    assert m.flatten(major=MatrixOrder.Row) == (1, 2, 3, 4, 5, 6, 7, 8, 9)
    assert m.flatten(major=MatrixOrder.Column) == (1, 4, 7, 2, 5, 8, 3, 6, 9)

  def test_transpose(self) -> None:
    m: Matrix3x3 = m3(
      1, 2, 3, 
      4, 5, 6,
      7, 8, 9
    )
    assert m.transpose() == m3(*m.flatten(major=MatrixOrder.Column))

  def test_multiplication(self) -> None:
    a = m3(
      5, 7, 9, 
      2, 3, 3, 
      8, 10, 2
    )

    b = m3(
      3, 10, 12,
      12, 1, 4,
      9, 10, 12,
    )

    c = a * b
    assert c == m3(
      180, 147, 196,
      69, 53, 72,
      162, 110, 160
    )

  def test_addition(self) -> None:
    a = m3(
      5, 7, 9,
      2, 3, 3,
      8, 10, 2
    )

    b = m3(
      3, 10, 12,
      12, 1, 4,
      9, 10, 12
    )

    c = a + b 
    assert c == m3(
      8, 17 , 21,
      14, 4, 7, 
      17, 20, 14
    )

  def test_subtraction(self) -> None:
    a = m3(
      5, 7, 9,
      2, 3, 3,
      8, 10, 2
    )

    b = m3(
      3, 10, 12,
      12, 1, 4,
      9, 10, 12
    )

    c = a - b
    assert c == m3(
      2, -3, -3, 
      -10, 2, -1,
      -1, 0, -10
    ) 

  def test_determinate(self) -> None:
    a = m3(
      1, 2, 3, 
      4, 5, 6, 
      7, 8, 9
    )

    b = m3(
      5, 7, 9,
      2, 3, 3,
      8, 10, 2
    )

    c = m3(
      3, 10, 12,
      12, 1, 4,
      9, 10, 12
    )

    assert Matrix3x3.identity().det() == 1.0
    assert a.det() == 0
    assert b.det() == -16
    assert c.det() == 168

  def test_adjugate(self) -> None:
    a = m3(
      1, 2, 3, 
      4, 5, 6, 
      7, 8, 9
    )
    assert a.adj() == m3(
      -3, 6, -3,
      6, -12, 6,
      -3, 6, -3
    )

  def test_inverse(self) -> None:
    a = m3(
      5, 7, 9,
      2, 3, 3,
      8, 10, 2
    )

    b = m3(
      3, 10, 12,
      12, 1, 4,
      9, 10, 12
    )

    assert a.inverse() == m3(
      1.5, -4.75, 0.375,
      -1.25, 3.875, -0.1875,
      0.25, -0.375, -0.0625
    )

    round_it = lambda i: round(i, 6)
    assert b.inverse().map(round_it) == m3(
      -0.166667, 0, 0.166667,
      -0.642857, -0.428571, 0.785714,
      0.660714, 0.357143, -0.696429
    )
