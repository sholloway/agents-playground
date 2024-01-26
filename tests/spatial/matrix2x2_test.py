import pytest
from agents_playground.spatial.matrix.matrix import MatrixError, MatrixOrder
from agents_playground.spatial.matrix.matrix2x2 import Matrix2x2, m2
from agents_playground.spatial.vector2d import Vector2d

class TestMatrix2x2:
  def test_initialization(self) -> None:
    m: Matrix2x2 = m2(
      1, 2, 
      3, 4
    )
    n = Matrix2x2((
      (1, 2),
      (3, 4)
    ))
    assert m == n
    
  def test_at_index(self) -> None:
    m: Matrix2x2 = m2(
      1, 2, 
      3, 4
    )
    
    expected_value = 1
    for i in range(2):
      for j in range(2):
        assert m.i(i, j) == expected_value
        expected_value += 1

  def test_fill(self) -> None:
    assert Matrix2x2.fill(1) == m2(1, 1, 1, 1)
    assert Matrix2x2.fill(3.14) == m2(3.14, 3.14, 3.14, 3.14)

  def test_invalid_index(self) -> None:
    m = Matrix2x2.fill(1)
    for i in range(2):
      for j in range(2):
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
      m.i(2, 0)
    
    with pytest.raises(MatrixError):
      m.i(0, 2)

  def test_identity(self) -> None:
    i = Matrix2x2.identity()
    assert i == m2(
      1, 0, 
      0, 1, 
    )

  def test_flatten(self) -> None:
    m: Matrix2x2 = m2(
      1, 2, 
      3, 4
    )
    assert m.flatten(major=MatrixOrder.Row) == (1, 2, 3, 4)
    assert m.flatten(major=MatrixOrder.Column) == (1, 3, 2, 4)

  def test_transpose(self) -> None:
    m: Matrix2x2 = m2(
      1, 2, 
      3, 4
    )
    assert m.transpose() == m2(*m.flatten(major=MatrixOrder.Column))

  def test_to_vectors(self) -> None:
    a = m2(
      1, 2, 
      3, 4
    )

    assert a.to_vectors(MatrixOrder.Row) == (Vector2d(1,2), Vector2d(3,4))
    assert a.to_vectors(MatrixOrder.Column) == (Vector2d(1,3), Vector2d(2,4))

  def test_multiplication(self) -> None:
    a = m2(
      5, 7, 
      2, 3 
    )

    b = m2(
      3, 10,
      12, 1
    )

    c = a * b # type: ignore
    assert c == m2(
      99, 57,
      42, 23
    )

  def test_addition(self) -> None:
    a = m2(
      5, 7, 
      2, 3
    )

    b = m2(
      3, 10, 
      12, 1
    )

    c = a + b 
    assert c == m2(
      8, 17,
      14, 4
    )

  def test_subtraction(self) -> None:
    a = m2(
      5, 7, 
      2, 3
    )

    b = m2(
      3, 10,
      12, 1
    )

    c = a - b
    assert c == m2(
      2, -3,
      -10, 2
    ) 

  def test_determinate(self) -> None:
    a = m2(
      5, 7, 
      2, 3 
    )

    b = m2(
      3, 10,
      12, 1
    )

    assert Matrix2x2.identity().det() == 1.0
    assert a.det() == 1
    assert b.det() == -117

  def test_adjugate(self) -> None:
    a = m2(
      1, 2,
      3, 4
    )
    assert a.adj() == m2(
      4, -2,
      -3, 1
    )

  def test_inverse(self) -> None:
    a = m2(
      1, 2,
      3, 4
    )
    assert a.inverse() == m2(
      -2, 1,
      1.5, -0.5
    )