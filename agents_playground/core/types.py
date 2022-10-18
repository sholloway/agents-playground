"""
Module for defining types used by the core classes.
"""
from __future__ import annotations
from dataclasses import dataclass

from typing import List, NamedTuple, Tuple

# Time based Types
TimeInSecs = float
TimeInMS = float

# Units of Measure
MegaBytes = float
Percentage = float
Count = int

# Performance Related
Sample = int | float

# Coordinates
# Note the definition of CanvasLocation is driven by DPGs annoying 
# habit of inconsistent return types.
CanvasLocation = List[int] | Tuple[int, ...]
CellLocation = Tuple[int, int]

#Convenience tuples for working with grid coordinates. 
CoordinateComponent = int | float

class Coordinate(NamedTuple):
  x: CoordinateComponent
  y: CoordinateComponent

  def multiply(self, p: Coordinate) -> Coordinate:
    return Coordinate(self.x * p.x, self.y * p.y) 

  def to_tuple(self) -> Tuple[CoordinateComponent, CoordinateComponent]:
    return (self.x, self.y)

# Handling Size
Dimension = int | float

@dataclass(init=False)
class Size:
  width: Dimension
  height: Dimension

  def __init__(self, w=-1, h=-1) -> None:
    self.width = w
    self.height = h

# Dealing with rotations
Radians = float
Degrees = float

# Geometry
# TODO: Should probably create a new folder that contains both this and Vector.
class AABBox:
  """An axis-aligned bounding box."""
  def __init__(self, min: Coordinate, max: Coordinate) -> None:
    """ Creates an axis-aligned bounding box defined by two points.
    Args:
      - min: The left most, upper point.
      - max: The right most, lower point.
    """
    self._min: Coordinate = min
    self._max: Coordinate = max

  def point_in(self, point: Coordinate) -> bool:
    """Calculates if a given point is in the box."""
    return (self._min <= point.x and point.x <= self._max.x) \
      and (self._min.y <= point.y and point.y <= self._max.y)