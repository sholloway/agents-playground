from __future__ import annotations

# Convenience tuples for working with grid coordinates.
from typing import NamedTuple, Tuple

CoordinateComponent = int | float

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