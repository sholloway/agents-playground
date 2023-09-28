
from __future__ import annotations

from functools import partial
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
from agents_playground.spatial.matrix2x2 import det2
from agents_playground.spatial.matrix3x3 import Matrix3x3, m3
from agents_playground.spatial.vector3d import Vector3d
from agents_playground.spatial.vector4d import Vector4d

def m4(
  m00: MatrixType, m01: MatrixType, m02: MatrixType, m03: MatrixType,
  m10: MatrixType, m11: MatrixType, m12: MatrixType, m13: MatrixType,
  m20: MatrixType, m21: MatrixType, m22: MatrixType, m23: MatrixType,
  m30: MatrixType, m31: MatrixType, m32: MatrixType, m33: MatrixType
  ) -> Matrix[MatrixType]:
  data = ( 
    (m00, m01, m02, m03),
    (m10, m11, m12, m13),
    (m20, m21, m22, m23),
    (m30, m31, m32, m33)
  )
  return Matrix4x4[MatrixType](data)

class Matrix4x4(Matrix[MatrixType]):
  """
  An immutable 4 by 4 matrix. Internally the data is stored in a flattened 
  tuple in row-major form.
  """
  def __init__(self, data: RowMajorNestedTuple) -> None:
    super().__init__(data, 4, 4)

  @staticmethod
  def identity() -> Matrix:
    return m4(
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1
    )
  
  @staticmethod
  def fill(value: MatrixType) -> Matrix[MatrixType]:
    return m4(
      value, value, value, value,
      value, value, value, value,
      value, value, value, value,
      value, value, value, value
    )
  
  def __repr__(self) -> str:
    row_one   = f"{','.join(map(str, self._data[0:4]))}"
    row_two   = f"{','.join(map(str, self._data[4:8]))}"
    row_three = f"{','.join(map(str, self._data[8:12]))}"
    row_four  = f"{','.join(map(str, self._data[12:16]))}"
    msg = f"Matrix4x4(\n\t{row_one}\n\t{row_two}\n\t{row_three}\n\t{row_four}\n)"
    return msg
    
  def transpose(self) -> Matrix[MatrixType]:
    """
    Returns the transpose of the matrix along its diagonal as a new matrix.

    For the matrix:
      | m00, m01, m02, m03 |
      | m10, m11, m12, m13 |
      | m20, m21, m22, m23 |
      | m30, m31, m32, m33 |

    Returns:
      | m00, m10, m20, m30 |
      | m01, m11, m21, m31 |
      | m02, m12, m22, m32 |
      | m03, m13, m23, m33 | 
    """
    i = partial(self.i)
    return m4(
      i(0,0), i(1,0), i(2,0), i(3,0),
      i(0,1), i(1,1), i(2,1), i(3,1),
      i(0,2), i(1,2), i(2,2), i(3,2),
      i(0,3), i(1,3), i(2,3), i(3,3),
    ) 

  def to_vectors(self, major: MatrixOrder) -> Tuple[Vector4d, ...]:
    """
    Returns the rows or columns of the matrix as a series of vectors.

    Args:
      - major (MatrixOrder): Determines the orientation of the vectors.
    """
    match major:
      case MatrixOrder.Row:
        return (
          Vector4d(*self._data[0:4]),
          Vector4d(*self._data[4:8]),
          Vector4d(*self._data[8:12]),
          Vector4d(*self._data[12:16])
        )
      case MatrixOrder.Column:
        i = partial(self.i) 
        return (
          Vector4d(i(0,0), i(1,0), i(2,0), i(3,0)),
          Vector4d(i(0,1), i(1,1), i(2,1), i(3,1)),
          Vector4d(i(0,2), i(1,2), i(2,2), i(3,2)),
          Vector4d(i(0,3), i(1,3), i(2,3), i(3,3))
        )
  
  def __mul__(self, other: object) -> Matrix:
    """
    Multiply this matrix by another matrix, scalar, or vector. 

    Returns
      this * other
    """
    if isinstance(other, Matrix4x4):
      # A new matrix is created by multiplying the rows of this matrix by 
      # the columns of the other matrix. So for C = A*B
      # Cij = Ai * Bj
      # So, Cij is the dot product of row Ai and column Bj.
      r = self.to_vectors(MatrixOrder.Row)
      c = other.to_vectors(MatrixOrder.Column)
      
      return m4(
        r[0]*c[0], r[0]*c[1], r[0]*c[2], r[0]*c[3],
        r[1]*c[0], r[1]*c[1], r[1]*c[2], r[1]*c[3],
        r[2]*c[0], r[2]*c[1], r[2]*c[2], r[2]*c[3],
        r[3]*c[0], r[3]*c[1], r[3]*c[2], r[3]*c[3]
      )
    elif isinstance(other, int) or isinstance(other, float):
      # Multiplying by a scalar. Apply the multiplication per value and 
      # create a new matrix.
      next_data = [other * x for x in self._data]
      return m4(*next_data)
    elif isinstance(other, Vector3d):
      raise NotImplementedError()
    else:
      error_msg = f"Cannot multiply an instance of Matrix4x4 by an instance of {type(other)}"
      raise MatrixError(error_msg)

  def __add__(self, other) -> Matrix:
    if isinstance(other, Matrix4x4):
      new_values = []
      for i in range(self.width):
        for j in range(self.height):
          new_values.append(self.i(i,j) + other.i(i,j))
      return m4(*new_values)
    else:
      raise NotImplementedError()

  def __sub__(self, other) -> Matrix:
    if isinstance(other, Matrix4x4):
      new_values = []
      for i in range(self.width):
        for j in range(self.height):
          new_values.append(self.i(i,j) - other.i(i,j))
      return m4(*new_values)
    else:
      raise NotImplementedError()
    
  @guard_indices
  def sub_matrix(self, row: int, col:int) -> Matrix3x3:
    indices = (0,1,2,3)
    filtered_rows = tuple(filter(lambda i: i != row, indices))
    filtered_cols = tuple(filter(lambda i: i != col, indices))
    sub_matrix_data = []
    for i in filtered_rows:
      for j in filtered_cols:
        sub_matrix_data.append(self.i(i,j))
    return m3(*sub_matrix_data)
  
  def det(self) -> float:
    """
    Calculate the determinate of the matrix using expansion of cofactors.
	  If there is a matrix A, [A] then there is a determinate of |A|.
	  
    For a 4x4 matrix [A], 
	  |A| = A00*|A00| - A01*|A01| + A02*|A02| - A03|A03|
    """
    i = partial(self.i)
    sm = partial(self.sub_matrix)
    return \
      i(0,0) * sm(0,0).det() - \
      i(0,1) * sm(0,1).det() + \
      i(0,2) * sm(0,2).det() - \
      i(0,3) * sm(0,3).det()

  def adj(self) -> Matrix:
    raise NotImplementedError()
    
  def inverse(self) -> Matrix[MatrixType]:
    """
    Returns the inverse of the matrix as a new matrix.
    
    The inverse of matrix A is defined as 1/A or A^-1 where
      A*A^-1 = A^-1*A = I
    
    For I, the identity matrix.
    A^-1 = 1/det(A) * adj(A)
    """
    # Algorithm Source: https://www.geometrictools.com/Documentation/LaplaceExpansionTheorem.pdf
    # Note: Naming conventions align to the paper.
    i = partial(self.i) # Alias for self.i to improve the code readability.
    
    s0 = det2(i(0,0), i(0,1), i(1,0), i(1,1))
    s1 = det2(i(0,0), i(0,2), i(1,0), i(1,2))
    s2 = det2(i(0,0), i(0,3), i(1,0), i(1,3))
    s3 = det2(i(0,1), i(0,2), i(1,1), i(1,2))
    s4 = det2(i(0,1), i(0,3), i(1,1), i(1,3))
    s5 = det2(i(0,2), i(0,3), i(1,2), i(1,3))

    c5 = det2(i(2,2), i(2,3), i(3,2), i(3,3))
    c4 = det2(i(2,1), i(2,3), i(3,1), i(3,3))
    c3 = det2(i(2,1), i(2,2), i(3,1), i(3,2))
    c2 = det2(i(2,0), i(2,3), i(3,0), i(3,3))
    c1 = det2(i(2,0), i(2,2), i(3,0), i(3,2))
    c0 = det2(i(2,0), i(2,1), i(3,0), i(3,1))

    determinate = s0*c5 - s1*c4 + s2*c3 + s3*c2 - s4*c1 + s5*c0
    if determinate == 0:
      raise MatrixError('Cannot calculate the inverse of a matrix that has a determinate of 0.')
    
    # Row 1
    m00 = i(1,1)*c5 - i(1,2)*c4 + i(1,3)*c3
    m01 = -i(0,1)*c5 + i(0,2)*c4 - i(0,3)*c3
    m02 = i(3,1)*s5 - i(3,2)*s4 + i(3,3)*s3
    m03 = -i(2,1)*s5 + i(2,2)*s4 - i(2,3)*s3
    
    # Row 2
    m10 = -i(1,0)*c5 + i(1,2)*c2 - i(1,3)*c1
    m11 = i(0,0)*c5 - i(0,2)*c2 + i(0,3)*c1
    m12 = -i(3,0)*s5 + i(3,2)*s2 - i(3,3)*s1
    m13 = i(2,0)*s5 - i(2,2)*s2 + i(2,3)*s1
    
    # Row 3
    m20 = i(1,0)*c4 - i(1,1)*c2 + i(1,3)*c0
    m21 = -i(0,0)*c4 + i(0,1)*c2 - i(0,3)*c0
    m22 = i(3,0)*s4 - i(3,1)*s2 + i(3,3)*s0
    m23 = -i(2,0)*s4 + i(2,1)*s2 - i(2,3)*s0
    
    # Row 4
    m30 = -i(1,0)*c3 + i(1,1)*c1 - i(1,2)*c0
    m31 = i(0,0)*c3 - i(0,1)*c1 + i(0,2)*c0
    m32 = -i(3,0)*s3 + i(3,1)*s1 - i(3,2)*s0
    m33 = i(2,0)*s3 - i(2,1)*s1 + i(2,2)*s0

    adjugate = m4(
      m00, m01, m02, m03,
      m10, m11, m12, m13,
      m20, m21, m22, m23,
      m30, m31, m32, m33
    )

    return adjugate * (1/determinate)

  def map(self, func: Callable[[MatrixType], MatrixType]) -> Matrix[MatrixType]:
    """Creates a new matrix by applying a function to every element in the matrix."""
    return m4(*[func(item) for item in self._data])
  
