from __future__ import annotations
from typing import Callable, Generic, Tuple

from agents_playground.spatial.matrix import (
  Matrix,
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

# Note: This is a convenience function for the more involved algorithms.
def det2(a: MatrixType, b: MatrixType, c: MatrixType, d: MatrixType) -> MatrixType:
    """
    Calculate the determinate of a 2x2 matrix represented as 4 numbers.
	  If there is a matrix A, [A] then there is a determinate of |A|.
    [A] = | a, b | 
			    | c, d |
	  |A| = ad - bc
    """
    return a * d - b*c

class Matrix2x2(Matrix[MatrixType]):
  def __init__(self, data: RowMajorNestedTuple) -> None:
    super().__init__(data, 2, 2)

  @staticmethod
  def fill(value: MatrixType) -> Matrix[MatrixType]:
    return m2(value, value, value, value)
  
  @staticmethod
  def identity() -> Matrix2x2:
    return m2(
      1, 0,
      0, 1
    )
  
  def new(self, data: RowMajorNestedTuple) -> Matrix[MatrixType]:
    """Create a new matrix with the same shape but with the provided data."""
    return Matrix2x2(data)
  
  def __repr__(self) -> str:
    row_one   = f"{','.join(map(str, self._data[0:2]))}"
    row_two   = f"{','.join(map(str, self._data[2:4]))}"
    msg = f"Matrix2x2(\n\t{row_one}\n\t{row_two}\n)"
    return msg
  
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
    # return self.i(0,0) * self.i(1,1) - self.i(0,1)*self.i(1,0)
    return det2(*self._data) 
  
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
    determinate: float = self.det()
    if determinate == 0:
      raise MatrixError('Cannot calculate the inverse of a matrix that has a determinate of 0.')
    return self.adj() * (1/determinate)
  
  def map(self, func: Callable[[MatrixType], MatrixType]) -> Matrix2x2[MatrixType]:
    """Creates a new matrix by applying a function to every element in the matrix."""
    return m2(*[func(item) for item in self._data])
    