from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeVar
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp import Maybe, Nothing

from agents_playground.spatial.coordinate import Coordinate, CoordinateComponentType
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
          Tutorial for EdgeFlip: https://jerryyin.info/geometry-processing-algorithms/half-edge/
          Rust Implementation: https://github.com/setzer22/blackjack/blob/main/blackjack_engine/src/mesh/halfedge.rs
          Hal-Edge Mesh Operations: https://docs.google.com/presentation/d/1U_uiZ3Jbc_ltHMhWBAvBDe4o0YKAAD3RNLXI3WwGmnE/edit#slide=id.g2704aba97d_0_201
          OpenMesh (C++): https://www.graphics.rwth-aachen.de/software/openmesh/intro/
          Implementation Tutorial: https://kaba.hilvi.org/homepage/blog/halfedge/halfedge.htm
          Paper: https://www.graphics.rwth-aachen.de/media/papers/directed.pdf

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

class MeshException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class MeshWindingDirection(Enum):
  CW = auto()
  CCW = auto()

# The ID of a half-edge. Is is a tuple of the vertex endpoint coordinates of 
# the form (origin, destination)
MeshHalfEdgeId = tuple[tuple[CoordinateComponentType, ...], tuple[CoordinateComponentType, ...]] 
MeshFaceId = int     # The ID of a face is the face instance hashed.

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
    self._vertices: dict[Coordinate, MeshVertex] = {}
    self._half_edges: dict[MeshHalfEdgeId, MeshHalfEdge] = {}
    self._faces: dict[MeshFaceId, MeshFace] = {}

    self._face_counter: Counter[int] = CounterBuilder.count_up_from_zero()
    self._vertex_counter: Counter[int] = CounterBuilder.count_up_from_zero()
    # Note: The edge counter is counting the number of edges, not the number of 
    #       half-edges.
    self._edge_counter: Counter[int] = CounterBuilder.count_up_from_zero()

  def num_vertices(self) -> int:
    return self._vertex_counter.value()
  
  def num_faces(self) -> int:
    return self._face_counter.value()
  
  def num_edges(self) -> int:
    return self._edge_counter.value()
  
  def vertex_at(self, location: Coordinate) -> MeshVertex:
    if location in self._vertices:
      return self._vertices[location]
    else:
      raise MeshException(f'The mesh does not have a vertex at {location}.')
  
  def add_polygon(self, vertex_coords: list[Coordinate]) -> None:
    # Given a polygon defined as a series of connected vertices, add the polygon
    # to the mesh.
    
    # 0. Enforce the constrains of the types of polygons that can be added to the mesh.
    self._enforce_polygon_requirements(vertex_coords)

    # 1. Convert the list of coordinates to MeshVertex instances and add them to 
    #    the mesh's master list of vertices. Keep a scoped copy for working with.
    vertices: list[MeshVertex] = self._register_vertices(vertex_coords)

    # 2. Create a face for the polygon.
    face = self._register_face()

    # 3. Create the half-edges.
    num_verts = len(vertices)
    first_vertex_index: int = 0
    last_vertex_index: int = len(vertices) -1
    first_inner_edge: MeshHalfEdge | None = None 
    previous_inner_edge: MeshHalfEdge | None = None 
    previous_outer_edge: MeshHalfEdge | None = None 

    for current_vertex_index in range(num_verts):
      # create a half-edge pair or get an existing one.
      next_vertex_index = first_vertex_index if current_vertex_index == last_vertex_index else current_vertex_index + 1
      inner_edge, outer_edge = self._register_half_edge_pair(vertices[current_vertex_index], vertices[next_vertex_index], face)
      

      # Handle linking internal half-edges.
      # Note: This will replace the previous/next links on any  
      #       existing half-edges. 
      if previous_inner_edge != None:
        # Not the first pass in the loop.
        inner_edge.previous_edge = previous_inner_edge
        previous_inner_edge.next_edge = inner_edge
      else:
        first_inner_edge = inner_edge

      previous_inner_edge = inner_edge
    
    # Handle closing the inner loop
    if previous_inner_edge != None:
      previous_inner_edge.next_edge = first_inner_edge 
      
    # TODO: handle linking the external edges.
    # This will require updating any existing boundary half-edges.
      
    return
  
  def _enforce_polygon_requirements(self, vertex_coords: list[Coordinate]) -> None:
    if len(vertex_coords) < 3:
      err_msg = f'A mesh can only have polygons with 3 vertices or more.\nA polygon with {len(vertex_coords)} was provided.'
      raise MeshException(err_msg)
    
    unique_vertex_cords = set(vertex_coords)
    if len(unique_vertex_cords) != len(vertex_coords):
      raise MeshException(f'Attempted to create a face with duplicate vertices.\n{vertex_coords}')

  def _register_vertices(self, vertex_coords: list[Coordinate]) -> list[MeshVertex]:
    """
    For a given list of vertex coordinates, register the vertices with the mesh.
    The edge on the vertex is not set during this operation.
    """
    vertices: list[MeshVertex] = []
    for vertex_coord in vertex_coords:
      if vertex_coord in self._vertices:
        # The mesh already has a vertex at these coordinates.
        # Grab a reference to the existing vertex.
        vertices.append(self._vertices[vertex_coord])
      else: 
        # This is a new vertex for the mesh.
        vertex = MeshVertex(vertex_coord)
        self._vertices[vertex_coord] = vertex
        vertices.append(vertex)
        self._vertex_counter.increment()
    return vertices
  
  def _register_face(self) -> MeshFace:
    face = MeshFace()
    face_id = self._face_counter.increment()
    self._faces[face_id] = face
    return face
  
  def _register_half_edge_pair(
    self, 
    current_vertex: MeshVertex, 
    next_vertex: MeshVertex, 
    face: MeshFace
  ) -> tuple[MeshHalfEdge, MeshHalfEdge]:
    """
    Creates a pair of half-edges. 

    Returns a tuple of (internal_half_edge, external_half_edge).
    """
    origin_loc = current_vertex.location.to_tuple()
    dest_loc = next_vertex.location.to_tuple()

    # The internal edge is the one we've got to determine if exists or not.
    if (origin_loc, dest_loc) in self._half_edges:
      # An external half-edge already exist for this edge already. 
      internal_edge = self._half_edges[(origin_loc, dest_loc)]
      internal_edge.face = face 

      # In this use case, the external edge is an internal edge on an existing face.
      if internal_edge.pair_edge != None:
        external_edge = internal_edge.pair_edge 
      else:
        raise MeshException('The pair of an existing half-edge is incorrectly not set.')
    else: 
      # Create a new edge.
      edge_indicator: int =  self._edge_counter.increment()
      internal_edge = MeshHalfEdge(
        edge_id = (origin_loc, dest_loc),
        edge_indicator = edge_indicator,
        origin_vertex = current_vertex, 
        face = face
      ) 
      current_vertex.edge = internal_edge # Assign the edge to the vertex since it's the first edge associated with it.

      external_edge = MeshHalfEdge(
        edge_id = (dest_loc, origin_loc),
        edge_indicator = edge_indicator,
        origin_vertex = next_vertex, 
        face = None
      ) 
    
      # Associate the pair of half-edges.
      internal_edge.pair_edge = external_edge
      external_edge.pair_edge = internal_edge

      # Register the half-edges by their vertex pairs.
      # Note: There is probably an elegant way to avoid this but I haven't found 
      # a simple solution for determining if an edge already exists yet.
      self._half_edges[internal_edge.edge_id] = internal_edge #type:ignore 
      self._half_edges[external_edge.edge_id] = external_edge #type:ignore 
  
    return (internal_edge, external_edge)

  """
  def add_polygon_old(self, vertex_coords: list[Coordinate]) -> None:
    # Given a list of coordinates, add a polygon to the mesh.

    # 1. Convert the list of coordinates to MeshVertex instances and add them to 
    #    the mesh's master list of vertices.
    vertices: list[MeshVertex] = [ MeshVertex(vc) for vc in vertex_coords ]
    self._vertices.extend(vertices)

    # 2. Create a face that represents the polygon being added and 
    #    add it to the mesh.
    face = MeshFace()
    self._faces.append(face)

    # 3. Create two linked lists. One for each direction of half-edges.
    #    Half-edges are split along the length of the edge. 
    half_edges_inner: list[MeshHalfEdge] = [] # Closest to the polygon.
    half_edges_outer: list[MeshHalfEdge] = [] 
    num_verts = len(vertices)
    for index in range(num_verts):
      # Is the vertex in the mesh already? Let's not think about this yet...
      
      # Grab a reference to current vertex.
      vert_a = vertices[index]

      # Depending grab the next vertex, unless we're at the end. 
      vert_b = vertices[0] if index == num_verts - 1 else vertices[index + 1]
        
      # Build the two half edges.
      half_edge_inner = MeshHalfEdge(origin_vertex=vert_a, face=face) # Closest to the polygon.
      half_edge_outer = MeshHalfEdge(origin_vertex=vert_b, face=face)

      # Associate the pair of half-edges with each other.
      half_edge_inner.pair_edge = half_edge_outer
      half_edge_outer.pair_edge = half_edge_inner

      # Associate the current vertex with the inner half-edge.
      vert_a.edge = half_edge_inner

      # Hang on two the two edges.
      half_edges_inner.append(half_edge_inner)
      half_edges_outer.append(half_edge_outer)

    # Associate the face with one of the half edges.
    face.boundary_edge = half_edges_inner[0]

    # 4. Set the next/previous for each of the edges to create a 
    # double, circular linked list.
    num_edges = num_verts - 1

    for current_index in range(num_edges):
      next_index = get_next_index(current_index, num_edges)
      last_index = get_last_index(current_index, num_edges)

      half_edges_inner[current_index].next_edge = half_edges_inner[next_index]
      half_edges_inner[current_index].previous_edge = half_edges_inner[last_index]

      half_edges_outer[current_index].next_edge = half_edges_outer[next_index]
      half_edges_outer[current_index].previous_edge = half_edges_outer[last_index]

    # 5. Add each of directional linked list to the mesh.
    self._half_edges.extend(half_edges_inner)
    self._half_edges.extend(half_edges_outer)
  """
    
  @property
  def winding(self) -> MeshWindingDirection:
    return self._winding

def get_next_index(current_index: int, num_edges: int) -> int:
  return 0 if current_index == num_edges - 1 else current_index + 1
 
def get_last_index(current_index, num_edges) -> int:
  last_position = num_edges - 1
  return last_position if current_index == 0 else current_index - 1 

@dataclass
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
  face_id: MeshFaceId | None = None # The unique ID of the face.

  boundary_edge: MeshHalfEdge | None = None # One of the face's edges.
  
  # If the face is a hole, then the boundary of the hole is stored in the same 
  # way as the external boundary. 
  inner_edge: MeshHalfEdge | None = None

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
  edge_id: MeshHalfEdgeId | None = None     # The unique ID of the edge.
  edge_indicator: int | None = None         # The order in which the edge was created. Rather, indicates that this half-edge is part of edge #N. 
  origin_vertex: MeshVertex | None = None   # Vertex at the end of the half-edge.
  pair_edge: MeshHalfEdge | None = None     # oppositely oriented adjacent half-edge
  face: MeshFace | None = None              # Face the half-edge borders
  next_edge: MeshHalfEdge | None = None     # Next half-edge around the face
  previous_edge: MeshHalfEdge | None = None # The last half-edge around the face

@dataclass
class MeshVertex:
  """
  Vertices in the half-edge data structure store their x, y, and z position as 
  well as a pointer to exactly one of the half-edges, which use the vertex as its starting point.
  """
  location: Coordinate             # Where the vertex is.
  edge: MeshHalfEdge | None = None # An edge that has this vertex as an origin.

  def __eq__(self, other: MeshVertex) -> bool:
    """Only compare the vertex coordinate when comparing MeshVertex instances."""
    return self.location.__eq__(other.location)
