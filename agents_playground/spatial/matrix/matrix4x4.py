from __future__ import annotations

from functools import partial
from math import pi, radians, tan

from agents_playground.spatial.matrix.matrix import (
  Matrix,
  MatrixError,
  MatrixType, 
  RowMajorNestedTuple
)
from agents_playground.spatial.matrix.matrix2x2 import det2
from agents_playground.spatial.matrix.matrix3x3 import m3
from agents_playground.spatial.types import Radians

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
  return Matrix4x4(data)

FOV_90 = radians(90)
FOV_72 = radians(72)

class Matrix4x4(Matrix[MatrixType]):
  """
  An immutable 4 by 4 matrix. Internally the data is stored in a flattened 
  tuple in row-major form.
  """
  def __init__(self, data: RowMajorNestedTuple) -> None:
    super().__init__(data, 4, 4)

  @staticmethod
  def projection(
    left: float, 
    right: float, 
    bottom: float, 
    top: float, 
    near: float, 
    far: float
  ) -> Matrix:
    m00 = 2*near/(right - left)
    m02 = (right + left)/(right - left)
    m11 = 2 * near/(top - bottom)
    m12 = (top + bottom)/(top - bottom)
    m22 = -(far + near)/(far - near)
    m23 = -2*far*near/(far - near)
    return m4(
      m00, 0,   m02, 0,
      0,   m11, m12, 0,
      0,   0,   m22, m23,
      0,   0,   -1,  0
    )
  
  @staticmethod
  def perspective(
    aspect_ratio: float, 
    v_fov: Radians = FOV_72, 
    near: float = 1.0, 
    far: float = 100.0
  ) -> Matrix:
    """
    Builds a projection matrix from a desired camera perspective. 

    Args:
      - aspect_ratio (float): The aspect ratio width / height.
      - v_fov (Radians): The camera angle from top to bottom.
      - near (float): The depth (negative z coordinate) of the near clipping plane.
      - far (float): The depth (negative z coordinate) of the far clipping plane.
    """
    top = near * tan(v_fov * 0.5)
    bottom = -top
    right = top * aspect_ratio
    left = -right 
    return Matrix4x4.projection(left, right, bottom, top, near, far)
    
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
  
  def new(self, *args:MatrixType) -> Matrix[MatrixType]:
    """Create a new matrix with the same shape but with the provided data."""
    return m4(*args)
  
  def new_size_smaller(self,  *args: MatrixType) -> Matrix[MatrixType]:
    """Provisions a matrix of a size smaller than the active matrix."""
    return m3(*args)
  
  def __repr__(self) -> str:
    row_one   = f"{','.join(map(str, self._data[0:4]))}"
    row_two   = f"{','.join(map(str, self._data[4:8]))}"
    row_three = f"{','.join(map(str, self._data[8:12]))}"
    row_four  = f"{','.join(map(str, self._data[12:16]))}"
    msg = f"Matrix4x4(\n\t{row_one}\n\t{row_two}\n\t{row_three}\n\t{row_four}\n)"
    return msg
  
  def det(self) -> float:
    """
    Calculate the determinate of the matrix using expansion of cofactors.
	  If there is a matrix A, [A] then there is a determinate of |A|.
	  
    For a 4x4 matrix [A], 
	  |A| = A00*|A00| - A01*|A01| + A02*|A02| - A03|A03|
    """
    i = partial(self.i)
    sm = partial(self.sub_matrix)
    determinate: float = \
      i(0,0) * sm(0,0).det() - \
      i(0,1) * sm(0,1).det() + \
      i(0,2) * sm(0,2).det() - \
      i(0,3) * sm(0,3).det()
    return determinate

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

    return adjugate * (1/determinate) # type: ignore