from __future__ import annotations

from typing import Protocol

from agents_playground.spatial.types import Coordinate, Radians

class Vector(Protocol):
  _i: float
  _j: float

  def scale(self, scalar: float) -> Vector:
    """Scale a vector by a scalar"""
    ...

  def to_point(self, vector_origin) -> Coordinate:
    """Returns a point that is on the vector at the end of the vector.
    
    Args
      - vector_origin: The point that the vector starts at.

    Returns
      A point that is offset from the vector_origin by the vector.
    """
    ...

  def rotate(self, angle: Radians) -> Vector:
    """Create a new vector by rotating it by an angle.
    
    Args
      - angle: The angle to rotate by provided in Radians.

    Returns
      A new vector created by applying the rotation.
    """
    ...

  def unit(self) -> Vector:
    """Returns the unit vector as a new vector."""
    ...

  def length(self) -> float:
    """Calculates the length of the vector."""
    ...

  def right_hand_perp(self) -> Vector:
    """Build a unit vector perpendicular to this vector."""
    ...
  
  def left_hand_perp(self) -> Vector:
    """Build a unit vector perpendicular to this vector."""
    ...