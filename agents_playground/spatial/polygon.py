from typing import List, Protocol

from agents_playground.spatial.vertex import Vertex

class Polygon(Protocol):
  """
  A lattice of vertices. 

  The vertices are wound counter-clockwise (CCW).
  """
  vertices: List[Vertex]