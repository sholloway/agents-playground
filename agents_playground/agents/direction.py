from __future__ import annotations

from enum import Enum
import math
from typing import NamedTuple

Radians = float

class Vector2D(NamedTuple):
  i: float
  j: float

  def scale(self, scalar: float) -> Vector2D:
    return Vector2D(self.i * scalar, self.j * scalar)

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

DIR_OPPOSITES: dict[Direction, Direction] = {
  Direction.NORTH : Direction.SOUTH,
  Direction.SOUTH : Direction.NORTH,
  Direction.EAST : Direction.WEST,
  Direction.WEST : Direction.EAST
}


DIR_ORIENTATION: dict[Direction, dict[Orientation, Direction]] = {
  Direction.NORTH : { Orientation.RIGHT : Direction.EAST, Orientation.LEFT: Direction.WEST, Orientation.BEHIND : Direction.SOUTH},
  Direction.EAST : { Orientation.RIGHT : Direction.SOUTH, Orientation.LEFT: Direction.NORTH, Orientation.BEHIND : Direction.WEST},
  Direction.SOUTH : { Orientation.RIGHT : Direction.WEST, Orientation.LEFT: Direction.EAST, Orientation.BEHIND : Direction.NORTH},
  Direction.WEST : { Orientation.RIGHT : Direction.NORTH, Orientation.LEFT: Direction.SOUTH, Orientation.BEHIND : Direction.EAST}
}

DIR_ROTATION: dict[Direction, float] = {
  Direction.EAST: 0.0, # 0
  Direction.NORTH: 1.5707963267948966, # Pi/2 or 90 Degrees
  Direction.WEST: math.pi, #pi or 180 degrees
  Direction.SOUTH: 4.71238898038469 # 3 * pi/ 2 or 270 degree
}