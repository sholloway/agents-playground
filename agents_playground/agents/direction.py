from __future__ import annotations

from enum import Enum
import math
from typing import NamedTuple

from agents_playground.agents.structures import Point

Radians = float

class Vector2D(NamedTuple):
  i: float
  j: float

  @staticmethod
  def from_points(start_point: Point, end_point: Point) -> Vector2D:
    """Create a new vector from two points"""
    return Vector2D(end_point.x - start_point.x, end_point.y - start_point.y)

  def scale(self, scalar: float) -> Vector2D:
    return Vector2D(self.i * scalar, self.j * scalar)

  def to_point(self, vector_origin) -> Point:
    """Returns a point that is on the vector at the end of the vector.
    
    Args
      - vector_origin: The point that the vector starts at.

    Returns
      A point that is offset from the vector_origin by the vector.
    """
    return Point(vector_origin.x + self.i, vector_origin.y + self.j)

  def rotate(self, angle: Radians) -> Vector2D:
    """Create a new vector by rotating it by an angle.
    
    Args
      - angle: The angle to rotate by provided in Radians.

    Returns
      A new vector created by applying the rotation.
    """
    return Vector2D(
      self.i * math.cos(angle) - self.j * math.sin(angle), 
      self.i * math.sin(angle) + self.j * math.cos(angle))

  def unit(self) -> Vector2D:
    """Returns the unit vector as a new vector."""
    l: float = self.length()
    return Vector2D(self.i/l, self.j/l)


  def length(self) -> float:
    return math.sqrt(self.i**2 + self.j**2)

  def right_hand_perp(self) -> Vector2D:
    """Build a unit vector perpendicular to this vector."""
    # need to handle the special cases of when i or j are zero
    return Vector2D(self.j, -self.i).unit()
  
  def left_hand_perp(self) -> Vector2D:
    """Build a unit vector perpendicular to this vector."""
    # need to handle the special cases of when i or j are zero
    return Vector2D(-self.j, self.i).unit()
  
class Direction:
  NORTH = Vector2D(0,1)
  EAST = Vector2D(1,0)
  SOUTH = Vector2D(0,-1)
  WEST = Vector2D(-1, 0)

class Orientation(Enum):
  LEFT = 'LEFT'
  RIGHT = 'RIGHT'
  BEHIND = 'BEHIND'

DIR_OPPOSITES: dict[Vector2D, Vector2D] = {
  Direction.NORTH : Direction.SOUTH,
  Direction.SOUTH : Direction.NORTH,
  Direction.EAST : Direction.WEST,
  Direction.WEST : Direction.EAST
}


DIR_ORIENTATION: dict[Vector2D, dict[Orientation, Vector2D]] = {
  Direction.NORTH : { Orientation.RIGHT : Direction.EAST, Orientation.LEFT: Direction.WEST, Orientation.BEHIND : Direction.SOUTH},
  Direction.EAST : { Orientation.RIGHT : Direction.SOUTH, Orientation.LEFT: Direction.NORTH, Orientation.BEHIND : Direction.WEST},
  Direction.SOUTH : { Orientation.RIGHT : Direction.WEST, Orientation.LEFT: Direction.EAST, Orientation.BEHIND : Direction.NORTH},
  Direction.WEST : { Orientation.RIGHT : Direction.NORTH, Orientation.LEFT: Direction.SOUTH, Orientation.BEHIND : Direction.EAST}
}

DIR_ROTATION: dict[Vector2D, float] = {
  Direction.EAST: 0.0, # 0
  Direction.NORTH: 1.5707963267948966, # Pi/2 or 90 Degrees
  Direction.WEST: math.pi, #pi or 180 degrees
  Direction.SOUTH: 4.71238898038469 # 3 * pi/ 2 or 270 degree
}