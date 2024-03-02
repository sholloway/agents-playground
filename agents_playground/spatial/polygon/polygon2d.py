
from typing import Protocol
from agents_playground.spatial.polygon.polygon import Polygon
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vector.vector2d import Vector2d
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
    
    # Loop through the edges on this polygon.
    # Determine if this polygon is on the positive side of line.
    for vert_a, vert_b in self.edges():
      outward_pointing = Vector2d.from_vertices(vert_a, vert_b).left_hand_perp()
      if self._which_side(other, vert_a, outward_pointing) > 0:
        # This polygon is entirely on the positive side of vert_a  + t * outward_pointing
        return False

    # 2. Test the edges of the other polygon for separation. 
    for vert_a, vert_b in other.edges():
      outward_pointing = Vector2d.from_vertices(vert_a, vert_b).left_hand_perp()
      if self._which_side(self, vert_a, outward_pointing) > 0:
        # This polygon is entirely on the positive side of vert_a  + t * outward_pointing
        return False

    return True
  
  def _which_side(self, polygon: Polygon, vertex: Vertex, projection_vector: Vector) -> int:
    """
    Determine if there is a separating axis between one of the vertices on the 
    provided polygon and vertex.

    The vertices of the provided polygon are projected to the form Vp + t * D.
    Where Vp is a vertex, t is a scalar, and D is a vector.

    The return value is +1 if all t > 0 and -1 if all t < 0. The value 0 is 
    returned if the line splits the polygon projection.
    
    Args: 
      - Polygon: The polygon to test.
      - Vertex: The vertex Vp.
      - projection_vector: The vector D.
    """

    positive: int = 0
    negative: int = 0

    for vert in polygon.vertices:
      # Project a vertex onto the line.
      t: float = projection_vector.dot(
        Vector2d(
          i = vert.coordinates[0] - vertex.coordinates[0], 
          j = vert.coordinates[1] - vertex.coordinates[1]
        )
      )

      if t > 0:
        positive += 1
      elif t < 0:
        negative += 1

      if positive and negative:
        # The polygon has vertices on both sides of the line so the line 
        # is not a separating axis.
        return 0
    return 1 if positive > 0 else -1

  
  
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