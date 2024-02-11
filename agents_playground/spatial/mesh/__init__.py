from __future__ import annotations
from abc import abstractmethod
from collections.abc import Callable
from typing import Protocol

from agents_playground.spatial.coordinate import Coordinate, CoordinateComponentType
from agents_playground.spatial.vector.vector import Vector

class MeshBuffer(Protocol):
  """
  A mesh buffer is a collection of vertices, vertex normals and an index that are arranged
  to be passed to a GPU rendering pipeline for rendering.
  """
  @property
  @abstractmethod
  def vertices(self) -> list[float]:
    ...
  
  @property
  @abstractmethod
  def vertex_normals(self) -> list[float]:
    ...
  
  @property
  @abstractmethod
  def vertex_index(self) -> list[int]:
    ...
 
  @property
  @abstractmethod
  def normal_index(self) -> list[int]:
    ...

# The ID of a half-edge. Is is a tuple of the vertex endpoint coordinates of 
# the form (origin, destination)
MeshHalfEdgeId = tuple[tuple[CoordinateComponentType, ...], tuple[CoordinateComponentType, ...]] 
MeshFaceId = int     # The ID of a face is the face instance hashed.

class MeshFaceLike(Protocol):
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
  face_id: MeshFaceId                           # The unique ID of the face.
  boundary_edge: MeshHalfEdgeLike | None = None # One of the face's edges.
  normal: Vector | None = None                  # The normal vector of the face.
  
  # If the face is a hole, then the boundary of the hole is stored in the same 
  # way as the external boundary. 
  inner_edge: MeshHalfEdgeLike | None = None

  @abstractmethod
  def count_boundary_edges(self) -> int:
    """Returns the number of edges associated with the face."""

  @abstractmethod
  def vertices(self) -> list[MeshVertexLike]:
    """Returns a list of vertices that compose the outer boarder of the face."""

  @abstractmethod
  def traverse_edges(self, actions: list[Callable[[MeshHalfEdgeLike], None]]) -> int:
    """
    Apply a series of methods to each edge that boarders the face.
    Returns the number of edges traversed.
    """

class MeshHalfEdgeLike(Protocol):
  """
  A half-edge is a half of an edge and is constructed by splitting an edge down 
  its length (not in half at it's midpoint). The two half-edges are referred to as a pair.

  Properties of a Half-edge:
  - May only be associated with a single face.
  - Stores a pointer to the that it face it borders.
  - Stores a pointer to the vertex that is it's endpoint.
  - Stores a point to its corresponding pair half-edge
  """
  edge_id: MeshHalfEdgeId                       # The unique ID of the edge.
  edge_indicator: int                           # The order in which the edge was created. Rather, indicates that this half-edge is part of edge #N. 
  origin_vertex: MeshVertexLike | None = None       # Vertex at the end of the half-edge.
  pair_edge: MeshHalfEdgeLike | None = None     # oppositely oriented adjacent half-edge
  face: MeshFaceLike | None = None              # Face the half-edge borders
  next_edge: MeshHalfEdgeLike | None = None     # Next half-edge around the face
  previous_edge: MeshHalfEdgeLike | None = None # The last half-edge around the face

class MeshVertexLike(Protocol):
  """
  Vertices in the half-edge data structure store their x, y, and z position as 
  well as a pointer to exactly one of the half-edges, which use the vertex as its starting point.
  """
  location: Coordinate                  # Where the vertex is.
  vertex_indicator: int                 # Indicates the order of creation.
  edge: MeshHalfEdgeLike | None = None  # An edge that has this vertex as an origin.
  normal: Vector | None = None          # The vertex normal.

  @abstractmethod
  def traverse_faces(self, actions: list[Callable[[MeshFaceLike], None]]) -> int:
    """
    Apply a series of methods to each face that boarders the vertex.
    Returns the number of faces traversed.
    """


class MeshLike(Protocol):
  @abstractmethod
  def add_polygon(self, vertex_coords: list[Coordinate]) -> None:
    """
    Add a polygon to the mesh.

    Args:
      - vertex_coords: The coordinates that form the boundary of the polygon.
    """

  @property
  @abstractmethod
  def vertices(self) -> list[MeshVertexLike]:
    """Returns the list of vertices that the mesh is composed of."""
  
  @property
  @abstractmethod
  def faces(self) -> list[MeshFaceLike]:
    """Returns the list of faces the mesh is composed of."""
  
  @property
  @abstractmethod
  def edges(self) -> list[MeshHalfEdgeLike]:
    """Returns the list of half-edges the list is composed of."""

  @abstractmethod
  def num_vertices(self) -> int:
    """Returns the number of unique vertices in the mesh."""
  
  @abstractmethod
  def num_faces(self) -> int:
    """Returns the number of unique faces in the mesh."""
  
  @abstractmethod
  def num_edges(self) -> int:
    """Returns the number of edges (a pair of half edges) in the mesh."""

  @abstractmethod
  def vertex_at(self, location: Coordinate) -> MeshVertexLike:
    """
    Returns a vertex located at the provided location.
    Throws a MeshException if no vertex exists.
    """

  @abstractmethod
  def half_edge_between(self, origin: Coordinate, destination: Coordinate) -> MeshHalfEdgeLike:
    """
    Returns a half-edge that leaves the provided origin and points to the destination. 
    Throws a MeshException if no half-edge exists.
    """

  @abstractmethod
  def deep_copy(self) -> MeshLike:
    """
    Returns a deep copy of the mesh. 
    No pointers are shared between the old mesh and the new mesh.
    """

  @abstractmethod
  def remove_face(self, face) -> None:
    """
    Removes a face from the mesh. Does not delete the associated edges or vertices.
    """

  @abstractmethod
  def calculate_face_normals(self) -> None:
    """
    Traverses every face in the mesh and calculates each normal.
    The normal is calculated using the winding order set for the mesh.
    Normals are stored on the individual faces.
    """

  @abstractmethod
  def calculate_vertex_normals(self) -> None:
    """
    Traverses every vertex in the mesh and calculates each normal.
    Normals are stored on the individual vertices.
    """

  @abstractmethod
  def pack(self) -> MeshBuffer:
    """
    Packs the mesh into a MeshBuffer.
    """