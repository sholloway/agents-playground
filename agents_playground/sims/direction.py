from enum import Enum
import math

class Direction(Enum):
  NORTH = 'NORTH'
  EAST = 'EAST'
  SOUTH = 'SOUTH'
  WEST = 'WEST'

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