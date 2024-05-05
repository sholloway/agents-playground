from dataclasses import dataclass
from operator import mul
from functools import reduce 
from math import cos, radians, sin
from typing import Self

from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4, m4
from agents_playground.spatial.types import Degrees
from agents_playground.spatial.vector import vector
from agents_playground.spatial.vector.vector import VECTOR_ROUNDING_PRECISION, Vector

def rotate_around(
  point_to_rotate: tuple[float,...], 
  rotation_point: tuple[float, ...], 
  axis: Vector,
  angle: Degrees
) -> tuple[float, ...]:
  """Convenance function to rotate a point around a vector.

  This function is equivalent to 
  t = Transformation()
  t.rotate_around(rotation_point, axis, angle)
  new_location = t.transform() * point_to_rotate

  Parameters:
    point_to_rotate: The point that shall be rotated.
    rotation_point: The origin of the vector to rotate around. 
    axis: The vector to rotate the point around.
    angle: The rotation amount specified in degrees.

  Returns:
  The new location of the point.
  """
  # Source: https://sites.google.com/site/glennmurray/Home/rotation-matrices-and-formulas
  # Establish aliases for the point to rotate's components.
  x = point_to_rotate[0]
  y = point_to_rotate[1]
  z = point_to_rotate[2]

  # Establish aliases for the point to rotate around's components.
  a = rotation_point[0]
  b = rotation_point[1]
  c = rotation_point[2]

  # Ensure that the axis has a length of 1.
  axis_norm = axis.unit()

  # Establish aliases for the vector to rotate around's components.
  u = axis_norm.i
  v = axis_norm.j
  w = axis_norm.k
  
  # Calculate the trig functions.
  rads = radians(angle)
  cosine = round(cos(rads), VECTOR_ROUNDING_PRECISION)
  one_minus_cosine = 1 - cosine
  sine = round(sin(rads), VECTOR_ROUNDING_PRECISION)

  # Establish aliases for the various products used in the rotation equations.
  u_sq = u * u
  v_sq = v * v
  w_sq = w * w

  au = a * u 
  av = a * v
  aw = a * w
  
  bu = b * u 
  bv = b * v 
  bw = b * w
  
  cu = c * u 
  cv = c * v 
  cw = c * w 
  
  ux = u * x
  uy = u * y  
  uz = u * z 
  
  vx = v * x 
  vy = v * y
  vz = v * z 
  
  wx = w * x 
  wy = w * y 
  wz = w * z

  # Evaluate the rotation equations.
  new_x = (a*(v_sq + w_sq) - u*(bv + cw - ux - vy - wz))*one_minus_cosine + x*cosine + (-cv + bw - wy + vz)*sine
  new_y = (b*(u_sq + w_sq) - v*(au + cw - ux - vy - wz))*one_minus_cosine + y*cosine + ( cu - aw + wx - uz)*sine
  new_z = (c*(u_sq + v_sq) - w*(au + bv - ux - vy - wz))*one_minus_cosine + z*cosine + (-bu + av - vx + uy)*sine
  return (new_x, new_y, new_z)

class Transformation:
  """Convenance class for working with Affine Transformations.

  A transformation is a set of affine transformations that are applied 
  to a vertex or vector in the order that they're added. 

  Example:
  To construct a transformation matrix of T = A*B*C:
  t = Transformation()
  t.mul(A).mul(B).mul(c)
  transformation_matrix = t.transform()
  """
  def __init__(self) -> None:
    self._stack: list[Matrix]             = []
    self._has_changed: bool               = False 
    self._cached_transform: Maybe[Matrix] = Nothing()

  def transform(self) -> Matrix:
    """Returns the combined transformation matrix.
    Multiplies all matrices from left to right with the first item added 
    considered the left most item.
    """
    if len(self._stack) < 1:
      return Matrix4x4.identity()
    
    if not self._cached_transform.is_something() or self._has_changed:
      self._cached_transform = Something(reduce(mul, self._stack))
      self._has_changed = False
    return self._cached_transform.unwrap()

  def clear(self) -> Self:
    """Resets the transformation stack to be empty.
    """
    self._stack.clear()
    self._has_changed = False
    self._cached_transform = Nothing()
    return self 
  
  def mul(self, m: Matrix) -> Self:
    """Places a matrix on the transformation stack."""
    self._stack.append(m)
    return self
  
  def identity(self) -> Self:
    """Places the identity matrix on the transformation stack
    """
    return self.mul(Matrix4x4.identity())
  
  def translate(self, v: Vector) -> Self:
    """Places a translation matrix on the transformation stack.

    Parameters:
      v: A vector to translate (i.e. move) an item along.
    """
    return self.mul(
      m4(
        1, 0, 0, v.i,
        0, 1, 0, v.j,
        0, 0, 1, v.k,
        0, 0, 0, 1
      )
    )
 
  def rotate_around_x(self, angle: Degrees) -> Self:
    """Places a rotation matrix on the transformation stack.

    Parameters:
      angle: An angle in degrees to rotate around the x-axis.
    """
    rads = radians(angle)
    c = cos(rads)
    s = sin(rads)
    return self.mul(
      m4(
        1, 0, 0, 0,
        0, c, -s, 0,
        0, s, c, 0,
        0, 0, 0, 1
      )
    )
  
  def rotate_around_y(self, angle: Degrees) -> Self:
    """Places a rotation matrix on the transformation stack.

    Parameters:
      angle: An angle in degrees to rotate around the y-axis.
    """
    rads = radians(angle)
    c = cos(rads)
    s = sin(rads)
    return self.mul(
      m4(
        c, 0, s, 0,
        0, 1, 0, 0,
        -s, 0, c, 0,
        0, 0, 0, 1
      )
    )
  
  def rotate_around_z(self, angle: Degrees) -> Self:
    """Places a rotation matrix on the transformation stack.

    Parameters:
      angle: An angle in degrees to rotate around the z-axis.
    """
    rads = radians(angle)
    c = cos(rads)
    s = sin(rads)
    return self.mul(
      m4(
        c, -s, 0, 0,
        s, c,  0, 0,
        0, 0,  1, 0,
        0, 0,  0, 1
      )
    )
    
  def rotate_around(self,
    rotation_point: tuple[float, ...], 
    axis: Vector,
    angle: Degrees
  ) -> Self:
    """Places a rotation matrix on the transformation stack.

    Parameters:
      rotation_point: The origin of the vector to rotate around. 
      angle: An angle in degrees to rotate.
      axis: The vector to perform a left-handed rotation around.
      angle: The rotation amount specified in degrees.
    """
    # Source: https://sites.google.com/site/glennmurray/Home/rotation-matrices-and-formulas

    # Establish aliases for the point to rotate around's components.
    a = rotation_point[0]
    b = rotation_point[1]
    c = rotation_point[2]

    # Ensure that the axis has a length of 1.
    axis_norm = axis.unit()

    # Establish aliases for the vector to rotate around's components.
    u = axis_norm.i
    v = axis_norm.j
    w = axis_norm.k
    
    # Calculate the trig functions.
    rads = radians(angle)
    cosine = round(cos(rads), VECTOR_ROUNDING_PRECISION)
    one_minus_cosine = 1 - cosine
    sine = round(sin(rads), VECTOR_ROUNDING_PRECISION)

    # Establish aliases for the various products used in the rotation equations.
    u_sq = u * u
    v_sq = v * v
    w_sq = w * w

    au = a * u 
    av = a * v
    aw = a * w
    
    bu = b * u 
    bv = b * v 
    bw = b * w
    
    cu = c * u 
    cv = c * v 
    cw = c * w 
    
    uv = u * v
    uw = u * w 
    vw = v * w 

    # Evaluate the components of the rotation transformation.
    m00 = u_sq + (v_sq + w_sq)*cosine 
    m01 = uv * one_minus_cosine - w * sine
    m02 = uw * one_minus_cosine + v * sine
    m03 = (a * (v_sq + w_sq) - u * (bv + cw))*one_minus_cosine + (bw - cv) * sine

    m10 = uv * one_minus_cosine + w * sine
    m11 = v_sq + (u_sq + w_sq)*cosine 
    m12 = vw * one_minus_cosine - u * sine 
    m13 = (b*(u_sq + w_sq) - v*(au + cw))*one_minus_cosine + (cu - aw) * sine 

    m20 = uw * one_minus_cosine - v * sine
    m21 = vw * one_minus_cosine + u * sine 
    m22 = w_sq + (u_sq + v_sq) * cosine
    m23 = (c * (u_sq + v_sq) - w * (au + bv))*one_minus_cosine + (av - bu) * sine

    return self.mul(
      m4(
        m00, m01, m02, m03,
        m10, m11, m12, m13,
        m20, m21, m22, m23,
        0,   0,   0,   1
      ) 
    )

  def scale(self, v: Vector) -> Self:
    """Places a translation matrix on the transformation stack.

    Parameters:
      v: A vector to scale (i.e. stretch or shrink) an item along.
    """
    return self.mul(
      m4(
        v.i, 0,   0,   0,
        0,   v.j, 0,   0, 
        0,   0,   v.k, 0,
        0,   0,   0,   1
      )
    )