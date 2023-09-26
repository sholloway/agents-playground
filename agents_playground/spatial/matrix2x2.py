from __future__ import annotations
from typing import Callable, Generic, Tuple

from agents_playground.spatial.matrix import (
  flatten, 
  guard_indices,
  MatrixError,
  MatrixOrder, 
  MatrixType, 
  RowMajorNestedTuple
)
from agents_playground.spatial.vector2d import Vector2d

def m2(
  m00: MatrixType, m01: MatrixType,
  m10: MatrixType, m11: MatrixType
) -> Matrix2x2[MatrixType]:
  data = (
    (m00, m01),
    (m10, m11)
  )
  return Matrix2x2(data)

class Matrix2x2(Generic[MatrixType]):
  def __init__(self, data: RowMajorNestedTuple) -> None:
    self._data = flatten(data, MatrixOrder.Row)
    self.width = 2
    self.height = 2

  @staticmethod
  def fill(value: MatrixType) -> Matrix2x2[MatrixType]:
    return m2(value, value, value, value)
  
  @staticmethod
  def identity() -> Matrix2x2:
    return m2(
      1, 0,
      0, 1
    )
  
  def __repr__(self) -> str:
    row_one   = f"{','.join(map(str, self._data[0:2]))}"
    row_two   = f"{','.join(map(str, self._data[2:4]))}"
    msg = f"Matrix2x2(\n\t{row_one}\n\t{row_two}\n)"
    return msg
  
  def __eq__(self, other: object) -> bool:
    if isinstance(other, Matrix2x2):
      return self._data.__eq__(other._data)
    else:
      raise MatrixError(f'Cannot compare a Matrix4x4 to a {type(other)}')

  @guard_indices(width=2, height=2)
  def i(self, row: int, col: int) -> MatrixType:
    """Finds the stored value in the matrix at matrix[i][j] using row-major convention."""
    # https://en.wikipedia.org/wiki/Row-_and_column-major_order
    return self._data[row * self.width + col]
  
  def flatten(self, major: MatrixOrder) -> Tuple[MatrixType, ...]:
    """
    Flattens the matrix into a tuple.

    Args:
      - major (MatrixOrder): Determines if the returned tuple will be in row-major
        or column-major order. The default is MatrixOrder.Column.

    Returns 
    The flattened tuple is either of the form:
    For the matrix:
      | m00, m01 |
      | m10, m11 |
  
    Row-Major
    (m00, m01, m02, m03)

    Column-Major
    (m00, m10, m20, m30)
    """
    match major:
      case MatrixOrder.Row:
        return self._data
      case MatrixOrder.Column:
        return (self.i(0,0), self.i(1,0), self.i(0,1), self.i(1,1))
      
  def transpose(self) -> Matrix2x2[MatrixType]:
    """
    Returns the transpose of the matrix along its diagonal as a new matrix.

    For the matrix:
      | m00, m01 |
      | m10, m11 |

    Returns:
      | m00, m10 |
      | m01, m11 |
    """
    return m2(
      self.i(0,0), self.i(1,0),
      self.i(0,1), self.i(1,1)
    ) 
  
  def to_vectors(self, major: MatrixOrder) -> Tuple[Vector2d, ...]:
    """
    Returns the rows or columns of the matrix as a series of vectors.

    Args:
      - major (MatrixOrder): Determines the orientation of the vectors.
    """
    match major:
      case MatrixOrder.Row:
        return (
          Vector2d(*self._data[0:2]),
          Vector2d(*self._data[2:4]),
        )
      case MatrixOrder.Column:
        return (
          Vector2d(self.i(0,0), self.i(1,0)),
          Vector2d(self.i(0,1), self.i(1,1)),
        )
  
  def __mul__(self, other: object) -> Matrix2x2:
    """
    Multiply this matrix by another matrix, scalar, or vector. 

    Returns
      this * other
    """
    if isinstance(other, Matrix2x2):
      # A new matrix is created by multiplying the rows of this matrix by 
      # the columns of the other matrix. So for C = A*B
      # Cij = Ai * Bj
      # So, Cij is the dot product of row Ai and column Bj.
      rows = self.to_vectors(MatrixOrder.Row)
      cols = other.to_vectors(MatrixOrder.Column)
      
      return m2(
        rows[0]*cols[0], rows[0]*cols[1],
        rows[1]*cols[0], rows[1]*cols[1]
      )
    elif isinstance(other, int) or isinstance(other, float):
      # Multiplying by a scalar. Apply the multiplication per value and 
      # create a new matrix.
      next_data = [other * x for x in self._data]
      return m2(*next_data)
    elif isinstance(other, Vector2d):
      raise NotImplementedError()
    else:
      error_msg = f"Cannot multiply an instance of Matrix2x2 by an instance of {type(other)}"
      raise MatrixError(error_msg)
  
  def det(self) -> float:
    """
    Calculate the determinate of the matrix.
	  If there is a matrix A, [A] then there is a determinate of |A|.
    [A] = | a, b | 
			    | c, d |
	  |A| = ad - bc
    """
    return self.i(0,0) * self.i(1,1) - self.i(0,1)*self.i(1,0)
  
  def adj(self) -> Matrix2x2:
    """
    Calculates the adjugate of the matrix.

    The adjugate of a matrix is the transpose of its cofactor matrix.
    """
    return m2(
      self.i(1,1), -self.i(0,1),
      -self.i(1,0), self.i(0,0)
    )
  
  def inverse(self) -> Matrix2x2[MatrixType]:
    """
    Returns the inverse of the matrix as a new matrix.
    
    The inverse of matrix A is defined as 1/A or A^-1 where
      A*A^-1 = A^-1*A = I
    
    For I, the identity matrix.
    A^-1 = 1/det(A) * adj(A)

    Which means:
    - A matrix A is invertible (inverse of A exists) only when det(A) ≠ 0.
    """
    return self.adj() * (1/self.det())
  
  def map(self, func: Callable[[MatrixType], MatrixType]) -> Matrix2x2[MatrixType]:
    """Creates a new matrix by applying a function to every element in the matrix."""
    return m2(*[func(item) for item in self._data])
    