from __future__ import annotations
from collections.abc import Callable

import copy
from dataclasses import dataclass, field
from enum import Enum, auto
import functools

from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.loaders.obj_loader import Obj, ObjPolygonVertex
from agents_playground.spatial.vector import vector
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import (
  UNSET_MESH_ID,
  MeshFaceDirection, 
  MeshFaceId, 
  MeshFaceLike, 
  MeshHalfEdgeId, 
  MeshHalfEdgeLike, 
  MeshLike,
  MeshVertexId, 
  MeshVertexLike
)
from agents_playground.spatial.vector import vector_from_points
from agents_playground.spatial.vector.vector import Vector

class MeshException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class MeshWindingDirection(Enum):
  CW = auto()
  CCW = auto()

MAX_TRAVERSALS = 1000

@dataclass
class MeshFace(MeshFaceLike):
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
  face_id: MeshFaceId                               # The unique ID of the face.
  normal_direction: MeshFaceDirection               # A direction to apply to the face's normal vector.
  boundary_edge_id: MeshHalfEdgeId = UNSET_MESH_ID  # The ID of one of the face's edges. 
  normal: Vector | None = None                      # The normal vector of the face.

  def boundary_edge(self, mesh: MeshLike) -> MeshHalfEdgeLike:
    if self.boundary_edge_id == UNSET_MESH_ID:
      raise MeshException(f'The boundary edge is not set for face {self.face_id}.')
    return mesh.edge(self.boundary_edge_id)
    
  def count_boundary_edges(self, mesh: MeshLike) -> int:
    """Returns the number of edges associated with the face."""
    return self.traverse_edges(mesh, [])
  
  def vertices(self, mesh: MeshLike) -> list[MeshVertexLike]:
    """Returns a list of vertices that compose the outer boarder of the face."""
    vertices: list[MeshVertexLike] = []
    def collect_vertices(half_edge: MeshHalfEdgeLike):
      if half_edge.origin_vertex is not None:
        vertices.append(half_edge.origin_vertex)
    self.traverse_edges(mesh, [collect_vertices])
    return vertices
  
  def traverse_edges(self, mesh: MeshLike, actions: list[Callable[[MeshHalfEdgeLike], None]]) -> int:
    """Apply a series of methods to each edge that boarders the face."""
    first_edge: MeshHalfEdgeLike = self.boundary_edge(mesh)
    current_edge: MeshHalfEdgeLike = first_edge
    edge_count = 0
    
    while True:
      edge_count += 1
      for action in actions:
        action(current_edge)
      if edge_count >= MAX_TRAVERSALS:
        raise MeshException(f'Attempting to traverse the edges around face {self.face_id} exceeded the maximum traversal threshold of {MAX_TRAVERSALS}.')
      elif current_edge.next_edge == None or current_edge.next_edge == first_edge:
        break 
      else:
        current_edge = current_edge.next_edge
    
    return edge_count

class MeshHalfEdge(MeshHalfEdgeLike):
  """
  Represents a half-edge.

  Note: The implementation is verbose to enable deepcopy.
  """

  """
  A half-edge is a half of an edge and is constructed by splitting an edge down 
  its length (not in half at it's midpoint). The two half-edges are referred to as a pair.

  Properties of a Half-edge:
  - May only be associated with a single face.
  - Stores a pointer to the that it face it borders.
  - Stores a pointer to the vertex that is it's endpoint.
  - Stores a point to its corresponding pair half-edge
  """
  def __new__(
    cls, 
    edge_id: MeshHalfEdgeId, 
    edge_indicator:int
  ):
    self = super().__new__(cls)  # Must explicitly create the new object 
    self.edge_id = edge_id    
    self.edge_indicator = edge_indicator 
    return self
  
  def __init__(
    self, 
    edge_id: MeshHalfEdgeId, 
    edge_indicator:int) -> None:
    self.edge_id: MeshHalfEdgeId                = edge_id        # The unique ID of the edge.
    self.edge_indicator: int                    = edge_indicator # The order in which the edge was created. Rather, indicates that this half-edge is part of edge #N. 
    self.origin_vertex: MeshVertexLike | None   = None           # Vertex at the end of the half-edge.
    self.pair_edge: MeshHalfEdgeLike | None     = None           # oppositely oriented adjacent half-edge
    self.face: MeshFaceLike | None              = None           # Face the half-edge borders
    self.next_edge: MeshHalfEdgeLike | None     = None           # Next half-edge around the face
    self.previous_edge: MeshHalfEdgeLike | None = None           # The last half-edge around the face
  
  def __getnewargs__(self):
    # Return the arguments that *must* be passed to __new__
    return (self.edge_id, self.edge_indicator)

  def __hash__(self) -> int:
    return hash((self.edge_id, self.edge_indicator))
  
  @staticmethod 
  def build(
    edge_id: MeshHalfEdgeId, 
    edge_indicator: int,               
    origin_vertex: MeshVertexLike | None = None,
    pair_edge: MeshHalfEdgeLike | None = None,
    face: MeshFaceLike | None = None,   
    next_edge: MeshHalfEdgeLike | None = None,
    previous_edge: MeshHalfEdgeLike | None = None
  ) -> MeshHalfEdgeLike:
    edge = MeshHalfEdge(edge_id, edge_indicator)
    edge.origin_vertex = origin_vertex
    edge.pair_edge = pair_edge
    edge.face = face 
    edge.next_edge = next_edge
    edge.previous_edge = previous_edge
    return edge
    
    
def init_outbound_edges() -> set[MeshHalfEdgeLike]:
  return set()

@dataclass
class MeshVertex(MeshVertexLike):
  """
  Vertices in the half-edge data structure store their x, y, and z position as 
  well as a pointer to exactly one of the half-edges, which use the vertex as its starting point.
  """
  location: Coordinate                  # Where the vertex is.
  vertex_indicator: int                 # Indicates the order of creation.
  
  # The list of all edges that have this vertex as an origin.
  # This isn't technically necessary, but is used to speed up constructing the mesh.
  outbound_edges: set[MeshHalfEdgeLike] = field(init = False, default_factory = init_outbound_edges)
  
  edge_id: MeshHalfEdgeId = UNSET_MESH_ID  # An edge that has this vertex as an origin.
  normal: Vector | None = None             # The vertex normal.

  @property
  def vertex_id(self) -> MeshVertexId:
    """Returns the hash of the location."""
    return hash(self.location)
  
  def edge(self, mesh: MeshLike) -> MeshHalfEdgeLike:
    """Returns the edge associated with the vertex"""
    return mesh.edge(self.edge_id)
  
  def add_outbound_edge(self, edge: MeshHalfEdgeLike) -> None:
    """Adds an edge to the list of outbound edges."""
    self.outbound_edges.add(edge)
  
  def traverse_faces(self, mesh: MeshLike, actions: list[Callable[[MeshFaceLike], None]]) -> int:
    """
    Apply a series of methods to each face that boarders the vertex.
    Returns the number of faces traversed.
    """
    if self.edge_id == None:
      raise MeshException(f'Attempted to traverse the faces on vertex {self.vertex_indicator}. It has no associated edges.')

    first_edge: MeshHalfEdgeLike = self.edge(mesh)
    current_edge: MeshHalfEdgeLike = first_edge
    edge_count = 0
    face_count = 0
    while True:
      edge_count += 1
      if current_edge.face is not None:
        face_count += 1
        for action in actions:
          action(current_edge.face)
      if edge_count >= MAX_TRAVERSALS:
        err_msg = f'Attempting to traverse the faces vertex {self.vertex_indicator}.\nExceeded the maximum traversal threshold of {MAX_TRAVERSALS}.'
        raise MeshException(err_msg)
      elif current_edge.pair_edge == None or \
        current_edge.pair_edge.next_edge == first_edge:
        # Done looping around the vertex.
        break 
      else:
        current_edge = current_edge.pair_edge.next_edge #type: ignore
    
    return face_count

  def __eq__(self, other: MeshVertex) -> bool:
    """Only compare the vertex coordinate when comparing MeshVertex instances."""
    return self.location.__eq__(other.location)
  
class HalfEdgeMesh(MeshLike):
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
    self._vertices: dict[MeshVertexId, MeshVertexLike] = {}
    self._half_edges: dict[MeshHalfEdgeId, MeshHalfEdgeLike] = {}
    self._faces: dict[MeshFaceId, MeshFaceLike] = {}
    self._vertices_requiring_adjustments: list[MeshVertexLike] = []

    # Counters that track how many components are in the mesh. 
    # These increase or decrease when items are added or removed.
    self._face_counter: Counter[int] = CounterBuilder.count_up_from_zero()
    self._vertex_counter: Counter[int] = CounterBuilder.count_up_from_zero()
    # Note: The edge counter is counting the number of edges, 
    #       not the number of half-edges.
    self._edge_counter: Counter[int] = CounterBuilder.count_up_from_zero()

    # Counters that produce IDs for mesh components. These only increase.
    self._face_id_generator: Counter[int] = CounterBuilder.count_up_from_zero()
    self._edge_id_generator: Counter[int] = CounterBuilder.count_up_from_zero()
    self._vertex_id_generator: Counter[int] = CounterBuilder.count_up_from_zero()

  def deep_copy(self) -> MeshLike:
    """
    Returns a deep copy of the mesh. 
    No pointers are shared between the old mesh and the new mesh.
    """
    return copy.deepcopy(self)
  
  def edge(self, edge_id: MeshHalfEdgeId) -> MeshHalfEdgeLike:
    """
    Returns the half-edge that is registered with the provided edge_id.
    """
    return self._half_edges[edge_id]
  

  @property
  def vertices(self) -> list[MeshVertexLike]:
    """Returns the list of vertices that the mesh is composed of."""
    return list(self._vertices.values())
  
  @property
  def faces(self) -> list[MeshFaceLike]:
    """Returns the list of faces the mesh is composed of."""
    return list(self._faces.values())
  
  @property
  def edges(self) -> list[MeshHalfEdgeLike]:
    """Returns the list of half-edges the list is composed of."""
    return list(self._half_edges.values())

  def num_vertices(self) -> int:
    return self._vertex_counter.value()
  
  def num_faces(self) -> int:
    return self._face_counter.value()
  
  def num_edges(self) -> int:
    return self._edge_counter.value()
  
  def vertex_at(self, location: Coordinate) -> MeshVertexLike:
    loc_hash = hash(location)
    if loc_hash in self._vertices:
      return self._vertices[loc_hash]
    else:
      raise MeshException(f'The mesh does not have a vertex at {location}.')
    
  def half_edge_between(self, origin: Coordinate, destination: Coordinate) -> MeshHalfEdgeLike:
    edge_id = hash((origin.to_tuple(), destination.to_tuple()))
    if edge_id in self._half_edges:
      return self._half_edges[edge_id]
    else: 
      raise MeshException(f'The mesh does not have an edge between vertices {edge_id}') 
  
  def add_polygon(
    self, 
    vertex_coords: list[Coordinate], 
    normal_direction: MeshFaceDirection = MeshFaceDirection.NORMAL
  ) -> None:
    """
    Given a polygon defined as a series of connected vertices, add the polygon
    to the mesh.

    Args:
      - vertex_coords: The vertices that form the boundary of the polygon.
      - normal_direction: A direction to apply to the face's normal when calculating the normal. This enables flipping the face.
    """
    
    # 0. Enforce the constrains of the types of polygons that can be added to the mesh.
    self._enforce_polygon_requirements(vertex_coords)

    # 1. Convert the list of coordinates to MeshVertex instances and add them to 
    #    the mesh's master list of vertices. Keep a scoped copy for working with.
    vertices: list[MeshVertexLike] = self._register_vertices(vertex_coords)

    # 2. Create a face for the polygon.
    face = self._register_face(normal_direction)

    # 3. Create the half-edges.
    num_verts = len(vertices)
    first_vertex_index: int = 0
    last_vertex_index: int = len(vertices) -1
    first_inner_edge: MeshHalfEdgeLike | None = None 
    first_outer_edge: MeshHalfEdgeLike | None = None 
    previous_inner_edge: MeshHalfEdgeLike | None = None 
    next_outer_edge: MeshHalfEdgeLike | None = None 

    for current_vertex_index in range(num_verts):
      # create a half-edge pair or get an existing one.
      next_vertex_index = first_vertex_index if current_vertex_index == last_vertex_index else current_vertex_index + 1
      new_edge, inner_edge, outer_edge = self._register_half_edge_pair(vertices[current_vertex_index], vertices[next_vertex_index], face)
      
      # Handle linking internal half-edges.
      if previous_inner_edge == None:
        # First pass. Record the first half-edge pair
        first_inner_edge = inner_edge
        first_outer_edge = outer_edge
      else:
        # Not the first pass in the loop. Connect the edges to form a double-linked list.
        inner_edge.previous_edge = previous_inner_edge
        previous_inner_edge.next_edge = inner_edge
        
        if new_edge:
          outer_edge.next_edge = next_outer_edge 
          next_outer_edge.previous_edge = outer_edge #type: ignore  
      
      # Track the current edge for chaining on the next iteration.
      previous_inner_edge = inner_edge
      next_outer_edge = outer_edge
   
    # 4. Assign the first inner edge to the polygon's face.
    if first_inner_edge is not None:
      face.boundary_edge_id = first_inner_edge.edge_id
    
    # 5. Handle closing the inner loop
    previous_inner_edge.next_edge = first_inner_edge      #type: ignore
    first_inner_edge.previous_edge = previous_inner_edge  #type: ignore

    # 6. Handle closing the outer loop
    # If the first_outer_edge.next_edge is not None, then it is part of another 
    # face. Ignore it.
    if first_outer_edge.next_edge == None:              #type: ignore
      first_outer_edge.next_edge = outer_edge           #type: ignore
      outer_edge.previous_edge = first_outer_edge       #type: ignore

    # 7. Adjust the border loops if needed.
    for vertex in self._vertices_requiring_adjustments:
      # 1. Find all the outbound edges from the vertex. ( <-- V --> )
      # The below line is scaling linearly, really slow, and is called 11,385 for the skull model.
      # 98% of the time in the entire add_polygon is spent here.
      # Perhaps, pull "7. Adjust the border loops if needed." into it's own function.
      # function caching may help. 
      # Breaking the add_polygon into subfunctions may also help.
      # Need to not do a full scan of all edges every single time.
      # Transitioning from pointers to indices would help but the complexity 
      # will go up.
      # outbound_edges: list[MeshHalfEdgeLike] =  [
      #   e for e in self._half_edges.values() 
      #   if e.origin_vertex == vertex
      # ]
      outbound_edges = vertex.outbound_edges
        
      if len(outbound_edges) == 0:
        continue # Skip this vertex.

      # 2. Find all inbound edges ( --> V <-- ) that are external (i.e. face == none).
      external_inbound: list[MeshHalfEdgeLike] = [ e.pair_edge for e in outbound_edges if e.pair_edge is not None and e.pair_edge.face is None]
      if len(external_inbound) == 0:
        continue # No external inbound half-edges so skip this vertex.

      # 3. Find the inbound and outbound external edges if any.
      external_outbound: list[MeshHalfEdgeLike] = [ e for e in outbound_edges if e.face is None]
      
      if len(external_outbound) == 1 and len(external_inbound) == 1:
        # Chain the inbound to the outbound ( Inbound --> V --> Outbound)
        external_inbound[0].next_edge = external_outbound[0]
        external_outbound[0].previous_edge = external_inbound[0]

    self._vertices_requiring_adjustments.clear()
    return
  
  def _enforce_polygon_requirements(self, vertex_coords: list[Coordinate]) -> None:
    if len(vertex_coords) < 3:
      err_msg = f'A mesh can only have polygons with 3 vertices or more.\nA polygon with {len(vertex_coords)} was provided.'
      raise MeshException(err_msg)
    
    unique_vertex_cords = set(vertex_coords)
    if len(unique_vertex_cords) != len(vertex_coords):
      raise MeshException(f'Attempted to create a face with duplicate vertices.\n{vertex_coords}')

  def _register_vertices(self, vertex_coords: list[Coordinate]) -> list[MeshVertexLike]:
    """
    For a given list of vertex coordinates, register the vertices with the mesh.
    The edge on the vertex is not set during this operation.
    """
    vertices: list[MeshVertexLike] = []
    for vertex_coord in vertex_coords:
      vertex_coord_hash = hash(vertex_coord)
      vertex: MeshVertexLike | None = self._vertices.get(vertex_coord_hash)
      if vertex is not None:
        # The mesh already has a vertex at these coordinates.
        # Grab a reference to the existing vertex.
        vertices.append(vertex)

        # Flag this existing vertex as needing to have its associated external 
        # half-edges next/previous references adjusted.
        # This is because adding a face to an existing face (i.e. with shared vertices)
        # Results in the external half-edges next/previous to be wrong.
        self._vertices_requiring_adjustments.append(vertex)
      else: 
        # This is a new vertex for the mesh.
        self._vertex_counter.increment()
        vertex = MeshVertex(
          location         = vertex_coord, 
          vertex_indicator = self._vertex_id_generator.increment()
        )
        self._vertices[vertex_coord_hash] = vertex
        vertices.append(vertex)
    return vertices
  
  def _register_face(self, normal_direction: MeshFaceDirection) -> MeshFaceLike:
    self._face_counter.increment()
    face_id = self._face_id_generator.increment()
    face = MeshFace(face_id=face_id, normal_direction=normal_direction)
    self._faces[face_id] = face
    return face
  
  def _register_half_edge_pair(
    self, 
    current_vertex: MeshVertexLike, 
    next_vertex: MeshVertexLike, 
    face: MeshFaceLike
  ) -> tuple[bool, MeshHalfEdgeLike, MeshHalfEdgeLike]:
    """
    Creates a pair of half-edges. 

    Returns a tuple of (new_edge, internal_half_edge, external_half_edge).
    """
    origin_loc = current_vertex.location.to_tuple()
    dest_loc = next_vertex.location.to_tuple()
    new_edge: bool 
    
    # The internal edge is the one we've got to determine if exists or not.
    new_edge = hash((origin_loc, dest_loc)) not in self._half_edges
    if new_edge:
      internal_edge, external_edge = self._create_new_edge(face, origin_loc, dest_loc, current_vertex, next_vertex)
    else:
      internal_edge, external_edge = self._use_existing_edge(face, origin_loc, dest_loc)
    
    return (new_edge, internal_edge, external_edge)
    
  def _use_existing_edge(self, face, origin_loc, dest_loc):
    internal_edge = self._half_edges[hash((origin_loc, dest_loc))]
    internal_edge.face = face  

    if internal_edge.pair_edge is None:
      raise MeshException('The pair of an existing half-edge is incorrectly not set.')
      
    return (internal_edge, internal_edge.pair_edge)
  
  def _create_new_edge(self, face, origin_loc, dest_loc, current_vertex, next_vertex):
    self._edge_counter.increment()
    edge_indicator: int = self._edge_id_generator.increment()

    internal_edge: MeshHalfEdgeLike = MeshHalfEdge.build(
      edge_id = hash((origin_loc, dest_loc)),
      edge_indicator = edge_indicator,
      origin_vertex = current_vertex, 
      face = face
    ) 

    # Assign the edge to the vertex if there isn't one associated with it already.
    if current_vertex.edge is None:
      current_vertex.edge = internal_edge 

    external_edge = MeshHalfEdge.build(
      edge_id = hash((dest_loc, origin_loc)),
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

    # Register the edges on their respective vertices.
    # This is to enable rapid lookups.
    current_vertex.add_outbound_edge(internal_edge)
    next_vertex.add_outbound_edge(external_edge)

    return (internal_edge, external_edge)

  @property
  def winding(self) -> MeshWindingDirection:
    return self._winding
  
  def remove_face(self, face: MeshFaceLike) -> None:
    """
    Removes a face from the mesh. Does not delete the associated edges or vertices.
    """ 
    face.traverse_edges(self, [set_face_to_none])
    if face.face_id in self._faces:
      self._faces.pop(face.face_id)
    del face
    self._face_counter.decrement()

  def calculate_face_normals(self, assume_planer=True) -> None:
    """
    Traverses every face in the mesh and calculates each normal.
    Normals are stored on the individual faces.

    Algorithm Details
    The algorithm used for calculating the face's normal is Newell's method 
    as documented in Graphic Gems III (algorithm) and IV (Glassner's Implementation).

    The areas of the projections of a polygon onto the Cartesian planes, 
    XY, YZ, and ZX, are proportional to the coefficients of the normal vector 
    to the polygon.

    Newell's method computes each one of these projected areas as the sum of the
    “signed” areas of the trapezoidal regions enclosed between each polygon edge
    and its projection onto one of the Cartesian axes.

    Let the n vertices of a polygon P be denoted by V1, V2,...Vn, 
    where:
      Vi =(Xi,Yi,Zi)
      i = 1, 2,...n.
      
    The plane equation ax + by + cz + d = 0 can be expressed as:
                    (X - P) ⋅ N = 0
  
    Where:
      X = (x, y, z)
      N = (a, b, c) is the normal to the plane
      P is an arbitrary reference point on the plane.

    The coefficients a, b, and c of the normal to the plane N are:
    a = ∑(yi — yi⊕1)(zi + zi⊕1) for i=1 to n
    b = ∑(zi — zi⊕1)(xi + xi⊕1) for i=1 to n
    c = ∑(xi — xi⊕1)(yi + yi⊕1)
    where ⊕ represents addition modulo n.

    The coefficient d is:
    d = -P ⋅ N
    
    where P is the arithmetic average of all the vertices of the polygon:
    P = 1/n ∑n Vi for i=1 to n
    """
    face: MeshFaceLike
    for face in self._faces.values():
      vertices = face.vertices(self)
      # For polygons that are known to be planer, you can just take the unit vector of the cross product.
      if assume_planer:
        vector_a: Vector = vector_from_points(vertices[0].location, vertices[1].location)
        vector_b: Vector = vector_from_points(vertices[0].location, vertices[len(vertices) - 1].location)
        face.normal = vector_a.cross(vector_b).unit() 
      else:
        # Don't assume the polygon is planer. Use Newell's method.
        # 1. Initialize the components of the normal to zero.
        i = j = k = 0.0

        # 2. Calculate the Normals of the Plane
        num_verts = len(vertices)
        for current_vert in range(num_verts):
          next_vert = (current_vert + 1) % num_verts 
          c0: Coordinate = vertices[current_vert].location
          c1: Coordinate = vertices[next_vert].location
          i += (c1[1] - c0[1]) * (c1[2] + c0[2])  #type: ignore
          j += (c1[2] - c0[2]) * (c1[0] + c0[0])  #type: ignore
          k += (c1[0] - c0[0]) * (c1[1] + c0[1])  #type: ignore
        face.normal = vector(i, j, k).unit()

      # Apply the face normal direction to potentially reverse the face's normal.
      # This enables flipping a triangle based on it's configuration.
      face.normal = face.normal.scale(face.normal_direction.value)
      
  def calculate_vertex_normals(self) -> None:
    """
    Traverses every vertex in the mesh and calculates each normal by averaging
    the normals of the adjacent faces. 
    Normals are stored on the individual vertices.
    """
    vertex: MeshVertexLike
    for vertex in self._vertices.values():
      # 1. Collect all of the normals of the adjacent faces.
      normals: list[Vector] = []
      
      def collect_normals(face: MeshFaceLike) -> None:
        if face.normal is None:
          raise MeshException(f'Attempted to access a missing normal on face {face.face_id}.')
        normals.append(face.normal)

      num_faces = vertex.traverse_faces([collect_normals])

      # 2. Calculate the sum of each vector component (i, j, k).
      sum_vectors = lambda v, v1: vector(v.i + v1.i, v.j + v1.j, v.k + v1.k)
      normal_sums = functools.reduce(sum_vectors,  normals)

      # 3. Create a vertex normal by taking the average of the face normals.
      vertex.normal = normal_sums.scale(1/num_faces).unit()

def set_face_to_none(half_edge: MeshHalfEdgeLike) -> None:
  half_edge.face = None

def obj_to_mesh(model: Obj) -> MeshLike:
  """
  Given an OBJ model, construct a half-edge mesh.
  Note: The polygons are added to the mesh as is. An additional triangulation step 
  must be done to convert the mesh to triangles if the mesh contains non-triangle polygons.
  """
  mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)

  # Add the faces.
  # print(f'The OBJ Model has {len(model.polygons)} polygons.')
  for poly_index, polygon in enumerate(model.polygons):
    # Find the vertices and convert ObjVertex3d to Coordinates.
    # Note: ObjVertex3d is of the form x,y,z,w
    vertices: list[Coordinate] = [ 
      Coordinate(*model.vertices[poly_vert.vertex - 1])
      for poly_vert in polygon.vertices
    ]

    # Bug: The winding thing is going to bite me here I think...
    # print(f'Adding polygon: {poly_index}', end='\r')
    mesh.add_polygon(vertices)
    
    # Set the vertex normals on the mesh.
    poly_vert: ObjPolygonVertex
    for poly_vert in polygon.vertices:
      pos = model.vertices[poly_vert.vertex - 1]
      normal: Vector3d = model.vertex_normals[poly_vert.normal - 1] #type: ignore
      mesh_vertex: MeshVertexLike = mesh.vertex_at(Coordinate(*pos))
      mesh_vertex.normal = normal
  # print('')
  return mesh
