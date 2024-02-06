from __future__ import annotations
from abc import abstractmethod

from dataclasses import dataclass
from enum import Enum, auto
from string import Template
from typing import Protocol, TypeVar
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
  face_id: MeshFaceId # The unique ID of the face.
  boundary_edge: MeshHalfEdge| None = None # One of the face's edges.
  
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
  edge_id: MeshHalfEdgeId                   # The unique ID of the edge.
  edge_indicator: int                       # The order in which the edge was created. Rather, indicates that this half-edge is part of edge #N. 
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
  location: Coordinate              # Where the vertex is.
  vertex_indicator: int             # Indicates the order of creation.
  edge: MeshHalfEdge | None = None  # An edge that has this vertex as an origin.

  def __eq__(self, other: MeshVertex) -> bool:
    """Only compare the vertex coordinate when comparing MeshVertex instances."""
    return self.location.__eq__(other.location)

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
    self._vertices_requiring_adjustments: list[MeshVertex] = []

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
    
  def half_edge_between(self, origin: Coordinate, destination: Coordinate) -> MeshHalfEdge:
    edge_id = (origin.to_tuple(), destination.to_tuple())
    if edge_id in self._half_edges:
      return self._half_edges[edge_id]
    else: 
      raise MeshException(f'The mesh does not have an edge between vertices {edge_id}') 
  
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
    first_outer_edge: MeshHalfEdge | None = None 
    previous_inner_edge: MeshHalfEdge | None = None 
    next_outer_edge: MeshHalfEdge | None = None 

    for current_vertex_index in range(num_verts):
      # create a half-edge pair or get an existing one.
      next_vertex_index = first_vertex_index if current_vertex_index == last_vertex_index else current_vertex_index + 1
      inner_edge, outer_edge = self._register_half_edge_pair(vertices[current_vertex_index], vertices[next_vertex_index], face)
      
      # Handle linking internal half-edges.
      if previous_inner_edge == None:
        # First pass. Record the first half-edge pair
        first_inner_edge = inner_edge
        first_outer_edge = outer_edge
      else:
        # Not the first pass in the loop. Connect the edges to form a double-linked list.
        inner_edge.previous_edge = previous_inner_edge
        previous_inner_edge.next_edge = inner_edge
        outer_edge.next_edge = next_outer_edge
        next_outer_edge.previous_edge = outer_edge #type: ignore

      # Track the current edge for chaining on the next iteration.
      previous_inner_edge = inner_edge
      next_outer_edge = outer_edge

    # 4. Assign the first inner edge to the polygon's face.
    face.boundary_edge = first_inner_edge
    
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
      outbound_edges: list[MeshHalfEdge] =  [e for e in self._half_edges.values() if e.origin_vertex == vertex]
      if len(outbound_edges) == 0:
        continue # Skip this vertex.

      # 2. Find all inbound edges ( --> V <-- ) that are external (i.e. face == none).
      external_inbound: list[MeshHalfEdge] = [ e.pair_edge for e in outbound_edges if e.pair_edge is not None and e.pair_edge.face is None]
      if len(external_inbound) == 0:
        continue # No external inbound half-edges so skip this vertex.

      # 3. Find the inbound and outbound external edges if any.
      external_outbound: list[MeshHalfEdge] = [ e for e in outbound_edges if e.face is None]
      
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

        # Flag this existing vertex as needing to have its associated external 
        # half-edges next/previous references adjusted.
        # This is because adding a face to an existing face (i.e. with shared vertices)
        # Results in the external half-edges next/previous to be wrong.
        self._vertices_requiring_adjustments.append(self._vertices[vertex_coord])
      else: 
        # This is a new vertex for the mesh.
        self._vertex_counter.increment()
        vertex = MeshVertex(location = vertex_coord, vertex_indicator=self._vertex_counter.value())
        self._vertices[vertex_coord] = vertex
        vertices.append(vertex)
    return vertices
  
  def _register_face(self) -> MeshFace:
    face_id = self._face_counter.increment()
    face = MeshFace(face_id=face_id)
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
      # Assign the edge to the vertex if there isn't one associated with it already.
      if current_vertex.edge is None:
        current_vertex.edge = internal_edge 

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
    
  @property
  def winding(self) -> MeshWindingDirection:
    return self._winding

class MeshPrinter(Protocol):
  @abstractmethod
  def print(self, mesh: Mesh) -> None:
    """Represents the mesh to STDOUT."""
  
class MeshTablePrinter(MeshPrinter):
  def print(self, mesh: Mesh) -> None:
    """
    Prints the mesh to STDOUT as a series of tables.
    """
    self._vertices_table(mesh)
    print('')
    self._faces_table(mesh)
    print('')
    self._edges_table(mesh)

  def _vertices_table(self, mesh: Mesh) -> None:
    print('Vertices')
    print('{:<10} {:<20} {:<10}'.format('Vertex', 'Coordinate', 'Incident Edge'))
    for k,v in mesh._vertices.items():
      print('{:<10} {:<20} {:<10}'.format(v.vertex_indicator, k.__repr__(), v.edge.edge_indicator )) #type: ignore

  def _faces_table(self, mesh: Mesh) -> None:
    print('Faces')
    print('{:<10} {:<10}'.format('Face', 'Boundary Edge'))
    for k, f in mesh._faces.items():
      print('{:<10} {:<10}'.format(k, f.boundary_edge.edge_indicator)) #type: ignore

  def _edges_table(self, mesh: Mesh) -> None:
    print('Half-edges')
    print('{:<10} {:<20} {:<10} {:<10} {:<10}'.format('Half-edge', 'Origin', 'Face', 'Next', 'Previous'))
    for e in mesh._half_edges.values():
      next_edge_indicator = e.next_edge.edge_indicator if e.next_edge is not None else 'None'
      previous_edge_indicator = e.previous_edge.edge_indicator if e.previous_edge is not None else 'None'
      face_id = e.face.face_id if e.face is not None else 'None'
      print('{:<10} {:<20} {:<10} {:<10} {:<10}'.format(e.edge_indicator, e.origin_vertex.location.__repr__(), face_id, next_edge_indicator, previous_edge_indicator)) #type: ignore

DIAGRAPH_TEMPLATE = """
digraph{
 # Note: Absolute positioning only works with neato and fdp
 # Set Node defaults
 node [shape=circle]
 
 # Vertex Positions
 ${vertices}
 
 # Half-Edges
 ${inner_half_edges}
 ${outer_half_edges}
}
"""

class MeshGraphVizPrinter(MeshPrinter):
  def print(self, mesh: Mesh) -> None:
    """
    Prints the mesh to STDOUT as a GraphViz digraph.
    
    Note: This prints the x,y coordinate. 
    If dealing with a 3d mesh you've got to decide which plane (XY or XZ) to visualize.
    """
    to_vert_loc = lambda v: f'v{v.vertex_indicator}[pos="{v.location[0]},{v.location[1]}!"]'
    vertices: list[str] = [ to_vert_loc(v) for v in mesh._vertices.values() ]

    to_inner_half_edge = lambda e: f'v{e.origin_vertex.vertex_indicator} -> v{e.pair_edge.origin_vertex.vertex_indicator} [label="1" color="green"]'
    inner_half_edges: list[str] = [ to_inner_half_edge(e) for e in mesh._half_edges.values() if e.face is not None]
    
    to_outer_half_edge = lambda e: f'v{e.origin_vertex.vertex_indicator} -> v{e.pair_edge.origin_vertex.vertex_indicator} [label="1" color="red" style="dashed"]'
    outer_half_edges: list[str] = [ to_outer_half_edge(e) for e in mesh._half_edges.values() if e.face is None]

    data: dict[str, str] = {
      'vertices': '\n '.join(vertices),
      'inner_half_edges': '\n '.join(inner_half_edges),
      'outer_half_edges': '\n '.join(outer_half_edges),
    }
    graph_viz: str = Template(DIAGRAPH_TEMPLATE).substitute(data)
    print(graph_viz)

