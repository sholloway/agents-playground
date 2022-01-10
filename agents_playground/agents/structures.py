from __future__ import annotations
from dataclasses import dataclass
from typing import NamedTuple, Union

"""
Convenience tuples for working with grid coordinates. 
"""

class Point(NamedTuple):
  x: Union[int, float]
  y: Union[int, float] 

  def multiply(self, p: Point) -> Point:
    return Point(self.x * p.x, self.y * p.y) 
  
Corner = Point

@dataclass(init=False)
class Size:
  width: Union[int, float]
  height: Union[int, float]

  def __init__(self, w=-1, h=-1) -> None:
    self.width = w
    self.height = h