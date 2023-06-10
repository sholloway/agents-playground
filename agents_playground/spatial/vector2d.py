from __future__ import annotations
import math
from agents_playground.spatial.types import Coordinate, Radians

from agents_playground.spatial.vector import Vector


class Vector2d(Vector):
  def __init__(self, i: float, j: float) -> None:
    super().__init__()
    self._i = i
    self._j = j

  @property
  def i(self) -> float:
    return self._i
  
  @property
  def j(self) -> float:
    return self._j
  
  @staticmethod
  def from_points(start_point: Coordinate, end_point: Coordinate) -> Vector2d:
    """Create a new vector from two points"""
    return Vector2d(end_point.x - start_point.x, end_point.y - start_point.y)

  def scale(self, scalar: float) -> Vector2d:
    """Scale a vector by a scalar"""
    return Vector2d(self._i * scalar, self._j * scalar)

  def to_point(self, vector_origin: Coordinate) -> Coordinate:
    """Returns a point that is on the vector at the end of the vector.
    
    Args
      - vector_origin: The point that the vector starts at.

    Returns
      A point that is offset from the vector_origin by the vector.
    """
    return Coordinate(vector_origin.x + self._i, vector_origin.y + self._j)

  def rotate(self, angle: Radians) -> Vector2d:
    """Create a new vector by rotating it by an angle.
    
    Args
      - angle: The angle to rotate by provided in Radians.

    Returns
      A new vector created by applying the rotation.
    """
    return Vector2d(
      self._i * math.cos(angle) - self._j * math.sin(angle), 
      self._i * math.sin(angle) + self._j * math.cos(angle))

  def unit(self) -> Vector2d:
    """Returns the unit vector as a new vector."""
    l: float = self.length()
    return Vector2d(self._i/l, self._j/l)

  def length(self) -> float:
    """Calculates the length of the vector."""
    return math.sqrt(self._i**2 + self._j**2)

  def right_hand_perp(self) -> Vector2d:
    """Build a unit vector perpendicular to this vector."""
    # need to handle the special cases of when i or j are zero
    return Vector2d(self._j, -self._i).unit()
  
  def left_hand_perp(self) -> Vector2d:
    """Build a unit vector perpendicular to this vector."""
    # need to handle the special cases of when i or j are zero
    return Vector2d(-self._j, self._i).unit()
  
  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(i={self._i},j={self._j})'