from __future__ import annotations
from abc import abstractmethod
import itertools

from typing import List, Protocol
from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vertex import Vertex

class Polygon(Protocol):
  """
  A lattice of vertices. 

  The vertices are wound counter-clockwise (CCW).
  """
  vertices: List[Vertex]

  def edges(self):
    """Iterates over the edges in a CCW fashion
    
    For example a 4 sided polygon
     V3      V2
    -------
    |     |
    |     |
    -------
    V0      V1

    Will iterate in the order
    1. (V0, V3)
    2. (V1, V0)
    3. (V2, V1)
    4. (V3, v2)
    """
    i = iter(self.vertices)
    prev = next(i)
    yield prev, self.vertices[-1]
    for item in i:
        yield item, prev
        prev = item

  @abstractmethod
  def intersect(self, other: Polygon) -> bool:
    """An intersection test between this polygon and another.
    
    Args:
      - other: The polygon to check for overlap with.

    Return:
      Returns True if the two polygons intersect.
  """