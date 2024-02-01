from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from agents_playground.fp import Maybe

from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.mesh import MeshBuffer

class Tesselator:
  """Given a spatial object, tesselates the object into triangles."""
  @staticmethod
  def from_landscape(landscape: Landscape) -> MeshBuffer:
    """
    Tesselates a landscape object into triangles.
    The triangles are returned in the same coordinate space that the landscape is in.

    Args:
      - landscape: The landscape to convert into triangles.

    Returns:
    A a mesh containing the Vertex Buffer with Vertex Normals, and index buffer.
    """
  
    """
    Steps:
    1. Build up an internal data structure that represents the triangles.
      What Data Structure?
        - Winged-edge
          https://en.wikipedia.org/wiki/Winged_edge
        - Quad-edge
          https://en.wikipedia.org/wiki/Quad-edge
        - Half-edge/Doubly linked face list (DLFL)
          https://en.wikipedia.org/wiki/Doubly_connected_edge_list
          http://www.sccg.sk/%7Esamuelcik/dgs/half_edge.pdf
          Explanation Video: https://www.youtube.com/watch?v=w5KOFgfx0CA 
          A decent fit for path finding across triangles.
          This is promising, however, I need to represent, disconnected graphs.
          Let's try doing this with the half-edge data structure to get started.

      Consider different tesselation approaches.
        - Naïve
          Just split a tile into two triangles with no regard to the larger mesh.
        - Treat the landscape as an unstructured grid, and tesselate the grid as a whole.
          https://en.wikipedia.org/wiki/Unstructured_grid
          - Ruppert's algorithm
            https://en.wikipedia.org/wiki/Ruppert%27s_algorithm

    2. Use this data structure to calculate the vertex normals.
      This is ultimately the problem I'm trying to solve. I need a data structure 
      that enables fast and easy traversal of the mesh to enable calculating the 
      normals of the connected faces per vertex.

      Additionally, the data structure selected for the internal traversal could 
      aid in future efforts to procedurally generate meshes, both landscape and otherwise.
    3. Pack the vertex data and normal data while building an index.
    4. Profit!
    """
    return None  # type: ignore


class MeshWindingDirection(Enum):
  CW = auto()
  CCW = auto()

class Mesh:
  """
  Represent a space partition using the half-edge/doubly-connected 
  edge list data structure. A mesh is composed of polygons. These could be 
  triangles but the data structure is generic and isn't limited to limited to 
  polygons of a specific category.

  A mesh can be traversed by: 
  - By connected faces.
  - By Edges
  """    
  def __init__(self, winding: MeshWindingDirection) -> None:
    self._winding: MeshWindingDirection = winding
    self._vertices: list[Coordinate] = []
    self._half_edges: list[MeshHalfEdge] = []
    self._faces: list[MeshFace] = []

  def add_polygon(self, vertices: list[Coordinate]) -> None:
    """Given a list of coordinates, add a polygon to the mesh."""
    pass

  @property
  def winding(self) -> MeshWindingDirection:
    return self._winding

class MeshFace:
  """
  A face is a polygon that has a boarder of edges or a hole.

  This implementation leverages the Half-edge/Doubly linked face list (DLFL) data structure.
  Resources
    - https://en.wikipedia.org/wiki/Doubly_connected_edge_list
    - http://www.sccg.sk/%7Esamuelcik/dgs/half_edge.pdf
    - Explanation Video: https://www.youtube.com/watch?v=w5KOFgfx0CA 
    - Book: Computational Geometry, Algorithms and Applications by Berg, Kreveld, Overmars, Schwarzkopf

  The half-edges that border a face form a circular, double linked list around its perimeter.
  This list can either be oriented clockwise or counter-clockwise around
  the face just as long as the same convention is used throughout.

  At a minimum, a face just needs a reference to one of it's boarder edges.
  Other data can be associated with faces. For example, face normals. 
  """
  boundary_edge: Maybe[MeshHalfEdge] # One of the face's edges.
  
  # If the face is a hole, then the boundary of the hole is stored in the same 
  # way as the external boundary. 
  inner_edge: Maybe[MeshHalfEdge]


@dataclass
class MeshHalfEdge:
  """
  A half-edge is a half of an edge and is constructed by splitting an edge down 
  its length (not in half at it's midpoint). The two half-edges are referred to as a pair.

  Properties of a Half-edge:
  - May only be associated with a single face.
  - Stores a pointer to the that it face it borders.
  - Stores a pointer to the vertex that is it's endpoint.
  - Stores a point to its corresponding pair half-edge
  """
  origin_vertex: MeshVertex   # Vertex at the end of the half-edge.
  pair_edge: MeshHalfEdge     # oppositely oriented adjacent half-edge
  face: MeshFace              # Face the half-edge borders
  next_edge: MeshHalfEdge     # Next half-edge around the face
  previous_edge: MeshHalfEdge # The last half-edge around the face

@dataclass
class MeshVertex:
  """
  Vertices in the half-edge data structure store their x, y, and z position as 
  well as a pointer to exactly one of the half-edges, which use the vertex as its starting point.
  """
  location: Coordinate # Where the vertex is.
  edge: MeshHalfEdge   # An edge that has this vertex as an origin.
  
