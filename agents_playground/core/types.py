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
  
Corner = Coordinate

Dimension = int | float

@dataclass(init=False)
class Size:
  width: Dimension
  height: Dimension

  def __init__(self, w=-1, h=-1) -> None:
    self.width = w
    self.height = h

Radians = float
Degrees = float