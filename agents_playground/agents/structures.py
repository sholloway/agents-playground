from __future__ import annotations
from dataclasses import dataclass
from typing import NamedTuple, Tuple, Union

"""
Convenience tuples for working with grid coordinates. 
"""
PointCoordinate = Union[int, float]
class Point(NamedTuple):
  x: PointCoordinate
  y: PointCoordinate

  def multiply(self, p: Point) -> Point:
    return Point(self.x * p.x, self.y * p.y) 

  def to_tuple(self) -> Tuple[PointCoordinate, PointCoordinate]:
    return (self.x, self.y)
  
Corner = Point

@dataclass(init=False)
class Size:
  width: Union[int, float]
  height: Union[int, float]

  def __init__(self, w=-1, h=-1) -> None:
    self.width = w
    self.height = h