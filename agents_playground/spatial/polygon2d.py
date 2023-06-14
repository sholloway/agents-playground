
from typing import Protocol
from agents_playground.spatial.polygon import Polygon
from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vector2d import Vector2d
from agents_playground.spatial.vertex import Vertex


class Polygon2d(Polygon, Protocol):
  """
  A lattice of 2D vertices. 

  The vertices are wound counter-clockwise (CCW).
  """

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
      outward_pointing = Vector2d.from_vertices(vert_a, vert_b).right_hand_perp()
      if (self._which_side(other, vert_a, outward_pointing) > 0):
        return False

    # 2. Test the edges of the other polygon for separation

    return True
  
  def _which_side(self, polygon: Polygon, vertex: Vertex, projection_vector: Vector) -> int:
    ...

  """
  Polygon
    Polygon2d
    - Frustum
      - Frustum2d
    - AABBox
      - AABBox2d

  Vertex
    - Vertex2d
  """