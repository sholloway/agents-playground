from __future__ import annotations
from abc import abstractmethod
from collections.abc import Callable
from enum import IntEnum
from typing import Protocol

from attr import dataclass

from agents_playground.fp import Maybe, Nothing
from agents_playground.spatial.coordinate import Coordinate, CoordinateComponentType
from agents_playground.spatial.vector.vector import Vector

class MeshBuffer(Protocol):
  """
  A mesh buffer is a collection of data and an index that are arranged
  to be passed to a GPU rendering pipeline for rendering.
  """
  @property
  @abstractmethod
  def data(self) -> list[float]:
    """
    The data in the buffer. The data could conceptually be anything but it in 
    reality it is a collection of floats. These floats tend to be vertex 
    coordinates, normals, and texture coordinates. The data is converted into a
    vertex buffer object (VBO)
    """
    ...
  
  @property
  @abstractmethod
  def index(self) -> list[int]:
    """The index of the data. This will be converted into a Vertex Buffer Index (VBI)."""
    ...

  @property
  @abstractmethod
  def count(self) -> int:
    """Returns the number of items (e.g. vertices are in the buffer.)"""

  @abstractmethod
  def print(self) -> None:
    """
    Writing the contents of the mesh buffer to STDOUT.
    """


# The ID of a half-edge. Is is the hash of a tuple of the vertex endpoint coordinates of 
# the form (origin, destination)
MeshHalfEdgeId = int 
MeshFaceId = int     
MeshVertexId = int   # The ID of a vertex is it's location hashed.
UNSET_MESH_ID: int = -1

class MeshFaceDirection(IntEnum):
  NORMAL = 1
  REVERSE = -1
  
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
  face_id: MeshFaceId                 # The unique ID of the face.
  normal_direction: MeshFaceDirection # A direction to apply to the face's normal vector.
  boundary_edge_id: MeshHalfEdgeId    # One of the face's edges. The value -1 is used to indicate the edge isn't set.
  normal: Vector | None               # The normal vector of the face.

  @abstractmethod
  def boundary_edge(self, mesh: MeshLike) -> MeshHalfEdgeLike:
    """
    Returns the associated boundary edge.
    """

  @abstractmethod
  def count_boundary_edges(self, mesh: MeshLike) -> int:
    """Returns the number of edges associated with the face."""

  @abstractmethod
  def vertices(self, mesh: MeshLike) -> tuple[MeshVertexLike, ...]:
    """Returns a list of vertices that compose the outer boarder of the face."""

  @abstractmethod
  def count_vertices(self, mesh: MeshLike) -> int:
    """Returns the number of vertices associated with the face."""

  @abstractmethod
  def traverse_edges(self, mesh: MeshLike, actions: list[Callable[[MeshHalfEdgeLike], None]]) -> int:
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
  edge_id: MeshHalfEdgeId           # The unique ID of the edge.
  edge_indicator: int               # The order in which the edge was created. Rather, indicates that this half-edge is part of edge #N. 
  origin_vertex_id: MeshVertexId    # Vertex at the end of the half-edge.
  pair_edge_id: MeshHalfEdgeId      # oppositely oriented adjacent half-edge
  face_id: MeshFaceId               # Face the half-edge borders
  next_edge_id: MeshHalfEdgeId      # Next half-edge around the face
  previous_edge_id: MeshHalfEdgeId  # The last half-edge around the face

  @abstractmethod
  def pair_edge(self, mesh: MeshLike) -> MeshHalfEdgeLike:
    """Returns a reference to the the associated pair edge."""

  @abstractmethod
  def origin_vertex(self, mesh: MeshLike) -> MeshVertexLike:
    """Returns a reference to the associated vertex at the edges origin."""
  
  @abstractmethod
  def next_edge(self, mesh: MeshLike) -> MeshHalfEdgeLike:
    """Returns a reference to the the associated next edge."""
  
  @abstractmethod
  def previous_edge(self, mesh: MeshLike) -> MeshHalfEdgeLike:
    """Returns a reference to the the associated previous edge."""
  
  @abstractmethod
  def face(self, mesh: MeshLike) -> MeshFaceLike:
    """Returns a reference to the the associated face."""

class MeshVertexLike(Protocol):
  """
  Vertices in the half-edge data structure store their x, y, and z position as 
  well as a pointer to exactly one of the half-edges, which use the vertex as its starting point.
  """
  location: Coordinate                  # Where the vertex is.
  vertex_indicator: int                 # Indicates the order of creation.
  edge_id: MeshHalfEdgeId               # An edge that has this vertex as an origin.
  normal: Vector | None = None          # The vertex normal.
  
  # The list of all edges that have this vertex as an origin.
  # This isn't technically necessary, but is used to speed up constructing the mesh.
  outbound_edge_ids: set[MeshHalfEdgeId]

  @property
  @abstractmethod
  def vertex_id(self) -> MeshVertexId:
    """Returns the hash of the location."""
  
  @abstractmethod
  def edge(self, MeshLike) -> MeshHalfEdgeLike:
    """Returns the edge associated with the vertex"""
  
  @abstractmethod
  def outbound_edges(self, mesh: MeshLike) -> tuple[MeshHalfEdgeLike, ...]:
    """Returns the list of all edges that have this vertex as an origin."""

  @abstractmethod
  def add_outbound_edge(self, edge_id: MeshHalfEdgeId) -> None:
    """Adds an edge to the list of outbound edges."""

  @abstractmethod
  def traverse_faces(
    self, 
    mesh: MeshLike, 
    actions: list[Callable[[MeshFaceLike], None]]
  ) -> int:
    """
    Apply a series of methods to each face that boarders the vertex.
    Returns the number of faces traversed.
    """

class MeshLike(Protocol):
  @abstractmethod
  def add_polygon(
    self, 
    vertex_coords: list[Coordinate], 
    normal_direction: MeshFaceDirection = MeshFaceDirection.NORMAL
  ) -> None:
    """
    Add a polygon to the mesh.

    Args:
      - vertex_coords: The coordinates that form the boundary of the polygon.
      - normal_direction: A direction to apply to the face's normal when calculating the normal. This enables flipping the face.
    """

  @property
  @abstractmethod
  def vertices(self) -> list[MeshVertexLike]:
    """Returns the list of vertices that the mesh is composed of."""
  
  @abstractmethod
  def vertex(self, vertex_id: MeshVertexId) -> MeshVertexLike:
    """Finds a vertex by its ID."""
  
  @property
  @abstractmethod
  def faces(self) -> list[MeshFaceLike]:
    """Returns the list of faces the mesh is composed of."""
  
  @abstractmethod
  def face(self, face_id: MeshFaceId) -> MeshFaceLike:
    """Returns the face associated with the provided face_id."""

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
  def edge(self, edge_id: MeshHalfEdgeId) -> MeshHalfEdgeLike:
    """
    Returns the half-edge that is registered with the provided edge_id.
    """

  @abstractmethod
  def fetch_edges(self, *edge_ids: MeshHalfEdgeId) -> tuple[MeshHalfEdgeLike, ...]:
    """Returns the edges for the provided list of edge_ids."""

  @abstractmethod
  def fetch_vertices(self, *vertex_ids: MeshVertexId) -> tuple[MeshVertexLike, ...]:
    """Returns the vertices with the corresponding vertex ids."""

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

class MeshPacker(Protocol):
  """Responsible for building a MeshBuffer from a mesh."""

  @abstractmethod
  def pack(self, mesh: MeshLike) -> MeshBuffer:
    """Given a mesh, packs it into a MeshBuffer."""

@dataclass 
class MeshData:
  """Collects all the related items for a single mesh."""
  alias: str 
  lod: int                            = 0
  next_lod_alias: Maybe[str]          = Nothing()
  mesh_previous_lod_alias: Maybe[str] = Nothing()
  mesh: Maybe[MeshLike]               = Nothing()
  vertex_buffer: Maybe[MeshBuffer]    = Nothing()
  normals_buffer: Maybe[MeshBuffer]   = Nothing()

class MeshRegistry:
  """
  Centralized storage for meshes.
  """
  def __init__(self) -> None:
    self._meshes: dict[str, MeshData] = {}

  def add_mesh(self, mesh_data: MeshData) -> None:
    self[mesh_data.alias] = mesh_data

  def __contains__(self, key: str) -> bool:
    return key in self._meshes
  def __getitem__(self, key: str) -> MeshData:
    return self._meshes[key]
  
  def __setitem__(self, key: str, value: MeshData) -> None:
    if isinstance(value, MeshData):
      self._meshes[key] = value
    else:
      raise TypeError(f'setitem on MeshRegistry cannot set a value of type {type(value)}.')
    
  def clear(self) -> None:
    self._meshes.clear()

  # Note: This may be a good spot to validate that the meshes 
  # are all ready to be bound to the bind groups.