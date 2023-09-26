from __future__ import annotations
from typing import Callable, Generic, Tuple

from agents_playground.spatial.matrix import (
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

class Matrix3x3(Generic[MatrixType]):
  def __init__(self, data: RowMajorNestedTuple) -> None:
    self._data = flatten(data, MatrixOrder.Row)
    self.width = 3
    self.height = 3 

  def __repr__(self) -> str:
    row_one   = f"{','.join(map(str, self._data[0:3]))}"
    row_two   = f"{','.join(map(str, self._data[3:6]))}"
    row_three = f"{','.join(map(str, self._data[6:9]))}"
    msg = f"Matrix3x3(\n\t{row_one}\n\t{row_two}\n\t{row_three}\n)"
    return msg
  
  def __eq__(self, other: object) -> bool:
    if isinstance(other, Matrix3x3):
      return self._data.__eq__(other._data)
    else:
      raise MatrixError(f'Cannot compare a Matrix4x4 to a {type(other)}')
    
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

  def to_vectors(self, major: MatrixOrder) -> Tuple[Vector3d, ...]:
    """
    Returns the rows or columns of the matrix as a series of vectors.

    Args:
      - major (MatrixOrder): Determines the orientation of the vectors.
    """
    match major:
      case MatrixOrder.Row:
        return (
          Vector3d(*self._data[0:3]),
          Vector3d(*self._data[3:6]),
          Vector3d(*self._data[6:9])
        )
      case MatrixOrder.Column:
        return (
          Vector3d(self.i(0,0), self.i(1,0), self.i(2,0)),
          Vector3d(self.i(0,1), self.i(1,1), self.i(2,1)),
          Vector3d(self.i(0,2), self.i(1,2), self.i(2,2))
        )
      
  def __mul__(self, other: object) -> Matrix3x3:
    if isinstance(other, Matrix3x3):
      # A new matrix is created by multiplying the rows of this matrix by 
      # the columns of the other matrix. So for C = A*B
      # Cij = Ai * Bj
      # So, Cij is the dot product of row Ai and column Bj.
      rows = self.to_vectors(MatrixOrder.Row)
      cols = other.to_vectors(MatrixOrder.Column)
      
      return m3(
        rows[0]*cols[0], rows[0]*cols[1], rows[0]*cols[2],
        rows[1]*cols[0], rows[1]*cols[1], rows[1]*cols[2],
        rows[2]*cols[0], rows[2]*cols[1], rows[2]*cols[2]
      )
    if isinstance(other, int) or isinstance(other, float):
      # Multiplying by a scalar. Apply the multiplication per value and 
      # create a new matrix.
      next_data = [other * x for x in self._data]
      return m3(*next_data)
    else:
      raise NotImplementedError()
    
  def __add__(self, other) -> Matrix3x3:
    if isinstance(other, Matrix3x3):
      new_values = []
      for i in range(self.width):
        for j in range(self.height):
          new_values.append(self.i(i,j) + other.i(i,j))
      return m3(*new_values)
    else:
      raise NotImplementedError()
    
  def __sub__(self, other) -> Matrix3x3:
    if isinstance(other, Matrix3x3):
      new_values = []
      for i in range(self.width):
        for j in range(self.height):
          new_values.append(self.i(i,j) - other.i(i,j))
      return m3(*new_values)
    else:
      raise NotImplementedError()
    
  @guard_indices(width=3, height=3)
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
      | m00, m01, m02 |
      | m10, m11, m12 |
      | m20, m21, m22 |
  
    Row-Major
    (m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22)

    Column-Major
    (m00, m10, m20, m01, m11, 21, m02, m12, m22)
    """
    match major:
      case MatrixOrder.Row:
        return self._data
      case MatrixOrder.Column:
        return (
          self.i(0,0), self.i(1,0), self.i(2,0),
          self.i(0,1), self.i(1,1), self.i(2,1),
          self.i(0,2), self.i(1,2), self.i(2,2)
        )
      
  def transpose(self) -> Matrix3x3[MatrixType]:
    """
    Returns the transpose of the matrix along its diagonal as a new matrix.

    For the matrix:
      | m00, m01, m02 |
      | m10, m11, m12 |
      | m20, m21, m22 |

    Returns:
      | m00, m10, m20 |
      | m01, m11, m21 |
      | m02, m12, m22 |
    """
    return m3(
      self.i(0,0), self.i(1,0), self.i(2,0),
      self.i(0,1), self.i(1,1), self.i(2,1),
      self.i(0,2), self.i(1,2), self.i(2,2)
    ) 
      
  @guard_indices(width=3, height=3)
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
    adj(A) = | +(a11a22 − a12a21) −(a01a22 − a02a21) +(a01a12 − a02a11) |
             | −(a10a22 − a12a20) +(a00a22 − a02a20) −(a00a12 − a02a10) |
             | +(a10a21 − a11a20) −(a00a21 − a01a20) +(a00a11 − a01a10) |

    Source: https://www.geometrictools.com/Documentation/LaplaceExpansionTheorem.pdf
    """
    m00 = self.i(1,1) * self.i(2,2) - self.i(1,2) * self.i(2,1)
    m01 = -(self.i(0,1)*self.i(2,2) - self.i(0,2)*self.i(2,1))
    m02 = self.i(0,1)*self.i(1,2) - self.i(0,2)*self.i(1,1)
    
    m10 = -(self.i(1,0)*self.i(2,2) - self.i(1,2)*self.i(2,0))
    m11 = self.i(0,0)*self.i(2,2) - self.i(0,2)*self.i(2,0)
    m12 = -(self.i(0,0)*self.i(1,2) - self.i(0,2)*self.i(1,0))
    
    m20 = self.i(1,0)*self.i(2,1) - self.i(1,1)*self.i(2,0)
    m21 = -(self.i(0,0)*self.i(2,1) - self.i(0,1)*self.i(2,0))
    m22 = self.i(0,0)*self.i(1,1) - self.i(0,1)*self.i(1,0)

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
    return self.adj() * (1/self.det())
  
  def map(self, func: Callable[[MatrixType], MatrixType]) -> Matrix3x3[MatrixType]:
    """Creates a new matrix by applying a function to every element in the matrix."""
    return m3(*[func(item) for item in self._data])