from __future__ import annotations
import itertools

from typing import List, Protocol

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

  def intersect(self, other: Polygon) -> bool:
    """An intersection test between this polygon and another.
    
    Args:
      - other: The polygon to check for overlap with.

    Return:
      Returns True if the two polygons intersect.

    Note:
    This intersection test leverages the Separating Axis Test (SAT) approach.
    See Resources
    Eberly, David. Intersection of Convex Objects: The Method of Separating Axes.
    https://www.geometrictools.com/Documentation/MethodOfSeparatingAxes.pdf

    Real-Time Rendering 3rd Edition by Akenine-Mooler, Haines, Hoffman

    Basically each side of the both polygons is projected onto a line. Then the 
    other polygon is tested to see if it overlaps the projected line.
    """
    # 1. Test this polygon for separation.
    # The polygons are wound in counter-clockwise order. 
    # So the projection interval is the range [T, 0] where T < 0.
    # If the other polygon is completely not overlapping the projected line
    # then the two polygons do not overlap.
    self_index: int = 0
    other_index:int = len(other.vertices) - 1

    # Loop through the rest of the edges on this polygon.
    for vert_a, vert_b in self.edges():
      pass

    # 2. Test the edges of the other polygon for separation

    return True


