from __future__ import annotations
from typing import NamedTuple, Tuple

# Dealing with rotations
Radians = float
Degrees = float

# Convenience tuples for working with grid coordinates.
CoordinateComponent = int | float

# TODO: Expand the definition of coordinate to have Coordinate, GridCoordinate, CanvasCoordinate 
class Coordinate(NamedTuple):
  x: CoordinateComponent
  y: CoordinateComponent

  def multiply(self, p: Coordinate) -> Coordinate:
    return Coordinate(self.x * p.x, self.y * p.y) 

  def shift(self, p:Coordinate) -> Coordinate:
    return Coordinate(self.x + p.x, self.y + p.y) 

  def to_tuple(self) -> Tuple[CoordinateComponent, CoordinateComponent]:
    return (self.x, self.y)
  
  def find_distance(self, other: Coordinate) -> float:
    """Finds the Manhattan distance between two locations."""
    return abs(self.x - other.x) + abs(self.y - other.y)
  
class Line2d(NamedTuple):
  """A two dimensional line defined by its endpoints A and B."""
  a: Coordinate
  b: Coordinate