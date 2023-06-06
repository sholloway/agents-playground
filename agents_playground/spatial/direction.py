from __future__ import annotations

from enum import Enum
import math

from agents_playground.spatial.vector2d import Vector2d
  
class Direction:
  NORTH = Vector2d(0,1)
  EAST = Vector2d(1,0)
  SOUTH = Vector2d(0,-1)
  WEST = Vector2d(-1, 0)

class Orientation(Enum):
  LEFT = 'LEFT'
  RIGHT = 'RIGHT'
  BEHIND = 'BEHIND'

DIR_OPPOSITES: dict[Vector2d, Vector2d] = {
  Direction.NORTH : Direction.SOUTH,
  Direction.SOUTH : Direction.NORTH,
  Direction.EAST : Direction.WEST,
  Direction.WEST : Direction.EAST
}


DIR_ORIENTATION: dict[Vector2d, dict[Orientation, Vector2d]] = {
  Direction.NORTH : { Orientation.RIGHT : Direction.EAST, Orientation.LEFT: Direction.WEST, Orientation.BEHIND : Direction.SOUTH},
  Direction.EAST : { Orientation.RIGHT : Direction.SOUTH, Orientation.LEFT: Direction.NORTH, Orientation.BEHIND : Direction.WEST},
  Direction.SOUTH : { Orientation.RIGHT : Direction.WEST, Orientation.LEFT: Direction.EAST, Orientation.BEHIND : Direction.NORTH},
  Direction.WEST : { Orientation.RIGHT : Direction.NORTH, Orientation.LEFT: Direction.SOUTH, Orientation.BEHIND : Direction.EAST}
}

DIR_ROTATION: dict[Vector2d, float] = {
  Direction.EAST: 0.0,                  # 0 Degrees
  Direction.NORTH: 1.5707963267948966,  # Pi/2 or 90 Degrees
  Direction.WEST: math.pi,              #pi or 180 degrees
  Direction.SOUTH: 4.71238898038469     # 3 * pi/ 2 or 270 degree
}