from __future__ import annotations
from typing import NamedTuple

"""
Convenience tuples for working with grid coordinates. 
"""
# Point = namedtuple('Point', ['x','y'])
class Point(NamedTuple):
  x: int
  y: int 


  def multiply(self, p: Point) -> Point:
    return Point(self.x * p.x, self.y * p.y) 
  
Corner = Point