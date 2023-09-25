from __future__ import annotations

from enum import Enum
import more_itertools
from typing import Generic, Tuple, TypeVar

from agents_playground.spatial.vector3d import Vector3d
from agents_playground.spatial.vector4d import Vector4d

T = TypeVar('T', int, float)
RowMajorNestedTuple = Tuple[Tuple[T, ...], ...]

class MatrixOrder(Enum):
  Row = 0
  Column = 1

def m4(m00: T, m01: T, m02: T, m03: T,
		m10: T, m11: T, m12: T, m13: T,
		m20: T, m21: T, m22: T, m23: T,
		m30: T, m31: T, m32: T, m33: T) -> Matrix4x4[T]:
  data = ( 
    (m00, m01, m02, m03),
    (m10, m11, m12, m13),
    (m20, m21, m22, m23),
    (m30, m31, m32, m33)
  )
  return Matrix4x4[T](data)

def flatten(data: RowMajorNestedTuple, major: MatrixOrder) -> Tuple[T, ...]:
  match major:
    case MatrixOrder.Row:
      return tuple(more_itertools.flatten(data))
    case MatrixOrder.Column:
      return ( 
        data[0][0], data[0][1], data[2][0], data[3][0], 
        data[0][1], data[1][1], data[2][1], data[3][1], 
        data[0][2], data[1][2], data[2][2], data[3][2], 
        data[0][3], data[1][3], data[2][3], data[3][3], 
      )

class Matrix4x4Error(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class Matrix4x4(Generic[T]):
  """
  An immutable 4 by 4 matrix. Internally the data is stored in a flattened 
  tuple in row-major form.
  """
  def __init__(self, data: RowMajorNestedTuple) -> None:
    self._data = flatten(data, MatrixOrder.Row)
    self.width = 4
    self.height = 4

  @staticmethod
  def identity() -> Matrix4x4:
    return m4(
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1
    )
  
  @staticmethod
  def fill(value: T) -> Matrix4x4[T]:
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
  
  def __eq__(self, other: object) -> bool:
    if isinstance(other, Matrix4x4):
      return self._data.__eq__(other._data)
    else:
      raise Matrix4x4Error(f'Cannot compare a Matrix4x4 to a {type(other)}')

  def i(self, row: int, col: int) -> T:
    """Finds the stored value in the matrix at matrix[i][j] using row-major convention."""
    # https://en.wikipedia.org/wiki/Row-_and_column-major_order
    if row >= 0 and row < 4 and col >= 0 and col < 4:
      index = row * self.width + col
      return self._data[index]
    else:
      general_msg = 'Attempted to access an element in a Matrix4x4 at an invalid index.'
      usage_msg = 'matrix.i(row, col) only accepts values in the range [0,3].'
      found_msg = f'found matrix.i(row={row}, col={col})'
      msg = f'{general_msg}\n{usage_msg}\n{found_msg}'
      raise Matrix4x4Error(msg)

  def flatten(self, major: MatrixOrder) -> Tuple[T, ...]:
    """
    Flattens the matrix into a tuple.

    Args:
      - major (MatrixOrder): Determines if the returned tuple will be in row-major
        or column-major order. The default is MatrixOrder.Column.

    Returns 
    The flattened tuple is either of the form:
    For the matrix:
      | m00, m01, m02, m03 |
      | m10, m11, m12, m13 |
      | m20, m21, m22, m23 |
      | m30, m31, m32, m33 |
  
    Row-Major
    (m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33)

    Column-Major
    (m00, m10, m20, m30, m01, m11, 21, m31, m02, m12m, m22m, m03, m13, m23, m33)
    """
    match major:
      case MatrixOrder.Row:
        return self._data
      case MatrixOrder.Column:
        return (
          self.i(0,0), self.i(1,0), self.i(2,0), self.i(3,0),
          self.i(0,1), self.i(1,1), self.i(2,1), self.i(3,1),
          self.i(0,2), self.i(1,2), self.i(2,2), self.i(3,2),
          self.i(0,3), self.i(1,3), self.i(2,3), self.i(3,3),
        )
  
  def transpose(self) -> Matrix4x4[T]:
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
    return m4(
      self.i(0,0), self.i(1,0), self.i(2,0), self.i(3,0),
      self.i(0,1), self.i(1,1), self.i(2,1), self.i(3,1),
      self.i(0,2), self.i(1,2), self.i(2,2), self.i(3,2),
      self.i(0,3), self.i(1,3), self.i(2,3), self.i(3,3),
    ) 

  def to_vectors(self, major: MatrixOrder) -> Tuple[Vector4d, ...]:
    match major:
      case MatrixOrder.Row:
        return (
          Vector4d(*self._data[0:4]),
          Vector4d(*self._data[4:8]),
          Vector4d(*self._data[8:12]),
          Vector4d(*self._data[12:16])
        )
      case MatrixOrder.Column:
        return (
          Vector4d(self.i(0,0), self.i(1,0), self.i(2,0), self.i(3,0)),
          Vector4d(self.i(0,1), self.i(1,1), self.i(2,1), self.i(3,1)),
          Vector4d(self.i(0,2), self.i(1,2), self.i(2,2), self.i(3,2)),
          Vector4d(self.i(0,3), self.i(1,3), self.i(2,3), self.i(3,3))
        )
  
  def __mul__(self, other: object) -> Matrix4x4:
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
      rows = self.to_vectors(MatrixOrder.Row)
      cols = other.to_vectors(MatrixOrder.Column)
      
      return m4(
        rows[0]*cols[0], rows[0]*cols[1], rows[0]*cols[2], rows[0]*cols[3],
        rows[1]*cols[0], rows[1]*cols[1], rows[1]*cols[2], rows[1]*cols[3],
        rows[2]*cols[0], rows[2]*cols[1], rows[2]*cols[2], rows[2]*cols[3],
        rows[3]*cols[0], rows[3]*cols[1], rows[3]*cols[2], rows[3]*cols[3]
      )
    elif isinstance(other, int) or isinstance(other, float):
      raise NotImplementedError()
    elif isinstance(other, Vector3d):
      raise NotImplementedError()
    else:
      error_msg = f"Cannot multiply an instance of Matrix4x4 by an instance of {type(other)}"
      raise Matrix4x4Error(error_msg)

  def __add__(self, other) -> Matrix4x4:
    if isinstance(other, Matrix4x4):
      new_values = []
      for i in range(self.width):
        for j in range(self.height):
          new_values.append(self.i(i,j) + other.i(i,j))
      return m4(*new_values)
    else:
      raise NotImplementedError()

  def __sub__(self, other) -> Matrix4x4:
    if isinstance(other, Matrix4x4):
      new_values = []
      for i in range(self.width):
        for j in range(self.height):
          new_values.append(self.i(i,j) - other.i(i,j))
      return m4(*new_values)
    else:
      raise NotImplementedError()

  def inverse(self) -> Matrix4x4[T]:
    """
    Returns the inverse of the matrix as a new matrix.
    
    The inverse of matrix A is defined as 1/A or A^-1 where
      A*A^-1 = A^-1*A = I
    
    For I, the identity matrix.
    """
    ...