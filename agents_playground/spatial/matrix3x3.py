from __future__ import annotations
from functools import partial, singledispatchmethod
from typing import Callable, Generic, Tuple

from agents_playground.spatial.matrix import (
  Matrix,
  MatrixError,
  flatten, 
  guard_indices,
  MatrixOrder, 
  MatrixType, 
  RowMajorNestedTuple
)
from agents_playground.spatial.matrix2x2 import Matrix2x2, m2
from agents_playground.spatial.vector3d import Vector3d

def m3(
  m00: MatrixType, m01: MatrixType, m02: MatrixType,
  m10: MatrixType, m11: MatrixType, m12: MatrixType,
  m20: MatrixType, m21: MatrixType, m22: MatrixType
) -> Matrix3x3[MatrixType]:
  data = ( 
    (m00, m01, m02),
    (m10, m11, m12),
    (m20, m21, m22)
  )
  return Matrix3x3[MatrixType](data)

class Matrix3x3(Matrix[MatrixType]):
  def __init__(self, data: RowMajorNestedTuple) -> None:
    super().__init__(data, 3, 3)

  def __repr__(self) -> str:
    row_one   = f"{','.join(map(str, self._data[0:3]))}"
    row_two   = f"{','.join(map(str, self._data[3:6]))}"
    row_three = f"{','.join(map(str, self._data[6:9]))}"
    msg = f"Matrix3x3(\n\t{row_one}\n\t{row_two}\n\t{row_three}\n)"
    return msg
    
  @staticmethod
  def identity() -> Matrix3x3:
    return m3(
      1, 0, 0,
      0, 1, 0,
      0, 0, 1
    )
  
  @staticmethod
  def fill(value: MatrixType) -> Matrix3x3[MatrixType]:
    return m3(
      value, value, value, 
      value, value, value, 
      value, value, value
    )

  def new(self, *args: MatrixType) -> Matrix[MatrixType]:
    """Create a new matrix with the same shape but with the provided data."""
    return m3(*args)
      
  @guard_indices
  def sub_matrix(self, row: int, col:int) -> Matrix2x2:
    indices = (0,1,2)
    filtered_rows = tuple(filter(lambda i: i != row, indices))
    filtered_cols = tuple(filter(lambda i: i != col, indices))
    sub_matrix_data = []
    for i in filtered_rows:
      for j in filtered_cols:
        sub_matrix_data.append(self.i(i,j))
    return m2(*sub_matrix_data)
    
  def det(self) -> float:
    """
    Calculate the determinate of the matrix using expansion of cofactors.
	  If there is a matrix A, [A] then there is a determinate of |A|.
	  
    For a 3x34 matrix [A], 
	  |A| = A00*|A00| - A01*|A01| + A02*|A02| 
    """
    return \
      self.i(0,0) * self.sub_matrix(0,0).det() - \
      self.i(0,1) * self.sub_matrix(0,1).det() + \
      self.i(0,2) * self.sub_matrix(0,2).det()
  
  def adj(self) -> Matrix3x3:
    """
    Calculates the adjugate of the matrix.

    The adjugate of a matrix is the transpose of its cofactor matrix.
    adj(A) = | +(a11a22 - a12a21) -(a01a22 - a02a21) +(a01a12 - a02a11) |
             | -(a10a22 - a12a20) +(a00a22 - a02a20) -(a00a12 - a02a10) |
             | +(a10a21 - a11a20) -(a00a21 - a01a20) +(a00a11 - a01a10) |

    Source: https://www.geometrictools.com/Documentation/LaplaceExpansionTheorem.pdf
    """
    i = partial(self.i)
    m00 = i(1,1)*i(2,2) - i(1,2)*i(2,1)
    m01 = -(i(0,1)*i(2,2) - i(0,2)*i(2,1))
    m02 = i(0,1)*i(1,2) - i(0,2)*i(1,1)
    
    m10 = -(i(1,0)*i(2,2) - i(1,2)*i(2,0))
    m11 = i(0,0)*i(2,2) - i(0,2)*i(2,0)
    m12 = -(i(0,0)*i(1,2) - i(0,2)*i(1,0))
    
    m20 = i(1,0)*i(2,1) - i(1,1)*i(2,0)
    m21 = -(i(0,0)*i(2,1) - i(0,1)*i(2,0))
    m22 = i(0,0)*i(1,1) - i(0,1)*i(1,0)

    return m3(
      m00, m01, m02,
      m10, m11, m12,
      m20, m21, m22
    )
  
  def inverse(self) -> Matrix3x3[MatrixType]:
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
  
  def map(self, func: Callable[[MatrixType], MatrixType]) -> Matrix3x3[MatrixType]:
    """Creates a new matrix by applying a function to every element in the matrix."""
    return m3(*[func(item) for item in self._data])