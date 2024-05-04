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
from agents_playground.spatial.vector.vector import Vector


class Transformation:
  """Convenance class for working with Affine Transformations.

  A transformation is a set of affine transformations that are applied 
  to a vertex or vector in the order that they're added.
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
    rads = radians(angle)
    c = cos(rads)
    s = sin(rads)
    return self.mul(
      m4(
        c, -s, 0, 0,
        s, c, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
      )
    )
    

  # def rotate(self) -> Matrix:
  #   """Returns the rotation matrix.
  #   """
  #   return m4()
    
  
  # def scale(self) -> Matrix:
  #   """Returns the scaling matrix.
  #   """
  #   return m4()