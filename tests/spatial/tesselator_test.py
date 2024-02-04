from typing import Callable
import pytest
from agents_playground.counter.counter import Counter, CounterBuilder

from agents_playground.fp import Nothing
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.landscape.constants import STANDARD_GRAVITY_IN_METRIC
from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile, TileCubicPlacement, TileCubicVerticesPlacement
from agents_playground.spatial.landscape.types import LandscapeGravityUOM, LandscapeMeshType
from agents_playground.spatial.mesh.tesselator import Mesh, MeshException, MeshFace, MeshHalfEdge, MeshVertex, MeshWindingDirection
from agents_playground.spatial.vector.vector3d import Vector3d
from agents_playground.uom import LengthUOM, SystemOfMeasurement

class TestTesselator:
  pass

@pytest.fixture
def lc() -> LandscapeCharacteristics:
  return LandscapeCharacteristics(
    mesh_type   = LandscapeMeshType.SquareTile,
    landscape_uom_system = SystemOfMeasurement.METRIC, 
    tile_size_uom = LengthUOM.METER,
    tile_width  = 1,
    tile_height = 1,
    tile_depth = 1,
  )

@pytest.fixture
def linear_landscape_strip(lc: LandscapeCharacteristics) -> Landscape:
  """
  Creates a landscape defined as a strip of tiles on the X-axis.
  """
  physicality = LandscapePhysicality(
    gravity_uom = LandscapeGravityUOM.MetersPerSecondSquared,
    gravity = STANDARD_GRAVITY_IN_METRIC
  )

  # A list of tile coordinates in the form (x,y,z,volume placement)
  tile_locations: list[tuple[int,...]] = [
    (0, 0, 0, TileCubicPlacement.BOTTOM),
    (1, 0, 0, TileCubicPlacement.BOTTOM),
    (2, 0, 0, TileCubicPlacement.BOTTOM),
    (3, 0, 0, TileCubicPlacement.BOTTOM),
    (4, 0, 0, TileCubicPlacement.BOTTOM),
    (5, 0, 0, TileCubicPlacement.BOTTOM),
  ]
  
  tiles: list[Tile] = [Tile(Coordinate(*t)) for t in tile_locations]

  return Landscape(
    file_characteristics = Nothing(),
    characteristics = lc,
    physicality = physicality,
    custom_attributes = {},
    tiles = { t.location : t for t in tiles} # Build a dict with the tile location as the key.
  )

@pytest.fixture
def polygon_a() -> list[Coordinate]:
  return[
    Coordinate(2, 3), # Vertex 1
    Coordinate(6, 6), # Vertex 2
    Coordinate(9, 3), # Vertex 3
    Coordinate(5, 1), # Vertex 4
  ]

@pytest.fixture   
def polygon_b() -> list[Coordinate]:
  return [
    Coordinate(9, 3),  # Shared Vertex 3
    Coordinate(6, 6),  # Shared Vertex 2
    Coordinate(10, 7), # Vertex 5
    Coordinate(13, 4), # Vertex 6
  ]

# TODO: This logic needs to live somewhere. 
def cubic_tile_to_vertices(tile: Tile, lc: LandscapeCharacteristics) -> list[Coordinate]:
  """
  Converts a tile to the vertices that define it.
  """
  # 1. Determine the vertices by the tile used on a unit cube.
  vertex_unit_vectors: tuple[Vector3d, ...] = TileCubicVerticesPlacement[tile.location[3]]

  # 2. Scale and translate the vertices to be the size specified by the landscape characteristics.
  x_offset = lc.tile_width * tile.location[0]
  y_offset = lc.tile_height * tile.location[1]
  z_offset = lc.tile_depth * tile.location[2]

  scaled_vertices: list[Coordinate] = \
    [ Coordinate(v.i*lc.tile_width + x_offset, v.j*lc.tile_height + y_offset, v.k* lc.tile_depth + z_offset) 
      for v in vertex_unit_vectors ]

  # 4. Return the vertices. 
  return scaled_vertices

class TestMesh:
  def test_polygon_winding(self) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CCW)
    assert mesh.winding == MeshWindingDirection.CCW

  def test_tile_to_vertices_with_bottom_tiles(self, lc: LandscapeCharacteristics) -> None:
    at_origin = Tile(Coordinate(0,0,0, TileCubicPlacement.BOTTOM))
    at_origin_tile_vertices: list[Coordinate] = cubic_tile_to_vertices(at_origin, lc)
    assert len(at_origin_tile_vertices) == 4
    assert at_origin_tile_vertices[0] == Coordinate(1, 0, 1) # F
    assert at_origin_tile_vertices[1] == Coordinate(1, 0, 0) # B
    assert at_origin_tile_vertices[2] == Coordinate(0, 0, 0) # C
    assert at_origin_tile_vertices[3] == Coordinate(0, 0, 1) # G

    shifted_on_x_axis_tile = Tile(Coordinate(4,0,0, TileCubicPlacement.BOTTOM))
    shifted_on_x_axis_tile_vertices: list[Coordinate] = cubic_tile_to_vertices(shifted_on_x_axis_tile, lc)
    assert len(shifted_on_x_axis_tile_vertices) == 4
    assert shifted_on_x_axis_tile_vertices[0] == Coordinate(5, 0, 1) # F
    assert shifted_on_x_axis_tile_vertices[1] == Coordinate(5, 0, 0) # B
    assert shifted_on_x_axis_tile_vertices[2] == Coordinate(4, 0, 0) # C
    assert shifted_on_x_axis_tile_vertices[3] == Coordinate(4, 0, 1) # G

    shifted_on_xy_plane = Tile(Coordinate(7, 0, -2, TileCubicPlacement.BOTTOM))
    shifted_on_xy_plane_vertices: list[Coordinate] = cubic_tile_to_vertices(shifted_on_xy_plane, lc)
    assert len(shifted_on_xy_plane_vertices) == 4
    assert shifted_on_xy_plane_vertices[0] == Coordinate(8, 0, -1) # F
    assert shifted_on_xy_plane_vertices[1] == Coordinate(8, 0, -2) # B
    assert shifted_on_xy_plane_vertices[2] == Coordinate(7, 0, -2) # C
    assert shifted_on_xy_plane_vertices[3] == Coordinate(7, 0, -1) # G

  # def test_construct_landscape_mesh(self, linear_landscape_strip: Landscape) -> None:
  #   assert len(linear_landscape_strip.tiles) == 6
  #   mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)

  #   for tile in linear_landscape_strip.tiles.values():
  #     tile_vertices = cubic_tile_to_vertices(tile, linear_landscape_strip.characteristics)
  #     mesh.add_polygon(tile_vertices)

    
  def test_single_2d_polygon_general_stats(self, polygon_a) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)

    # The general mesh stats.
    assert mesh.num_vertices() == 4
    assert mesh.num_faces() == 1
    assert mesh.num_edges() == 4

  def test_single_2d_polygon_verts(self, polygon_a) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)

    # All the vertices are in the mesh.
    for coordinate in polygon_a:
      assert mesh.vertex_at(coordinate) is not None 

  def test_single_2d_polygon_first_vertex(self, polygon_a) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)
    
    # Inspect the first vertex.
    v1 = mesh.vertex_at(Coordinate(2, 3))
    assert v1.location == Coordinate(2, 3)
    assert v1.edge.edge_indicator == 1                   #type:ignore 
    assert v1.edge.edge_id == ((2, 3), (6, 6))           #type:ignore 
    assert v1.edge.face is not None                      #type:ignore 
    assert v1.edge.pair_edge.edge_id == ((6, 6), (2, 3)) #type:ignore
    assert v1.edge.pair_edge.face is None                #type:ignore 
    assert v1.edge.pair_edge.origin_vertex.location == Coordinate(6, 6) #type:ignore 

  def test_single_2d_polygon_second_vertex(self, polygon_a) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)

    # Inspect the second vertex.
    v2 = mesh.vertex_at(Coordinate(6, 6))
    assert v2.location == Coordinate(6, 6)
    assert v2.edge.edge_indicator == 2                    #type:ignore 
    assert v2.edge.edge_id == ((6, 6), (9, 3))            #type:ignore 
    assert v2.edge.face is not None                       #type:ignore 
    assert v2.edge.pair_edge.edge_id == ((9, 3), (6, 6))  #type:ignore
    assert v2.edge.pair_edge.face is None                 #type:ignore 
    assert v2.edge.pair_edge.origin_vertex.location == Coordinate(9, 3) #type:ignore 
    
  def test_single_2d_polygon_third_vertex(self, polygon_a) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)
    # Inspect the third vertex.
    v3 = mesh.vertex_at(Coordinate(9, 3))
    assert v3.location == Coordinate(9, 3)
    assert v3.edge.edge_indicator == 3                    #type:ignore 
    assert v3.edge.edge_id == ((9, 3), (5,1))             #type:ignore 
    assert v3.edge.face is not None                       #type:ignore 
    assert v3.edge.pair_edge.edge_id == ((5, 1), (9, 3))  #type:ignore
    assert v3.edge.pair_edge.face is None                 #type:ignore 
    assert v3.edge.pair_edge.origin_vertex.location == Coordinate(5,1) #type:ignore 
    
  def test_single_2d_polygon_fourth_vertex(self, polygon_a) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)

    # Inspect the fourth vertex.
    v4 = mesh.vertex_at(Coordinate(5, 1))
    assert v4.location == Coordinate(5, 1)
    assert v4.edge.edge_indicator == 4                    #type:ignore 
    assert v4.edge.edge_id == ((5,1), (2, 3))             #type:ignore 
    assert v4.edge.face is not None                       #type:ignore 
    assert v4.edge.pair_edge.edge_id == ((2, 3), (5,1))   #type:ignore
    assert v4.edge.pair_edge.face is None                 #type:ignore 
    assert v4.edge.pair_edge.origin_vertex.location == Coordinate(2, 3) #type:ignore 

  def test_two_connected_2d_polygon_stats(self, polygon_a, polygon_b) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)
    mesh.add_polygon(polygon_b)
    assert mesh.num_vertices() == 6
    assert mesh.num_faces() == 2
    assert mesh.num_edges() == 7

  def test_two_connected_2d_polygon_verts(self, polygon_a, polygon_b) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)
    mesh.add_polygon(polygon_b)
    # All the vertices are in the mesh.
    for coordinate in polygon_a + polygon_b:
      assert mesh.vertex_at(coordinate) is not None 


  def test_two_connected_2d_polygon_existing_edges(self, polygon_a, polygon_b) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)
    mesh.add_polygon(polygon_b)

    # Inspect the edge between vertices 2 and 3. 
    # Adding the second polygon should have set the face on 
    # the external edge between vert 2 and 3 to Face ID #2.
    # It's twin should be associated with Face ID #1.
    half_edge_between_verts_2_3 = mesh.half_edge_between(Coordinate(9, 3), Coordinate(6, 6))
    assert half_edge_between_verts_2_3 is not None 
    assert half_edge_between_verts_2_3.edge_indicator == 2
    assert half_edge_between_verts_2_3.face.face_id == 2            #type: ignore
    assert half_edge_between_verts_2_3.pair_edge.face.face_id == 1  # type: ignore

  def test_inner_boundary_connectivity_face_1(self, polygon_a, polygon_b) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)
    mesh.add_polygon(polygon_b)

    # Verify that the face ID is the same as the dict key.
    face_1: MeshFace = mesh._faces[1] 
    assert face_1.face_id == 1

    # Verify that the inner half-edges are correct for Face 1.
    assert face_1.boundary_edge.edge_indicator == 1                                       #type: ignore
    assert face_1.boundary_edge.edge_id == ((2, 3),(6, 6))                                #type: ignore
    assert face_1.boundary_edge.next_edge.edge_indicator == 2                             #type: ignore
    assert face_1.boundary_edge.next_edge.edge_id == ((6, 6), (9, 3))                     #type: ignore
    assert face_1.boundary_edge.next_edge.next_edge.edge_indicator == 3                   #type: ignore
    assert face_1.boundary_edge.next_edge.next_edge.edge_id == ((9, 3), (5, 1))           #type: ignore
    assert face_1.boundary_edge.next_edge.next_edge.next_edge.edge_indicator == 4         #type: ignore
    assert face_1.boundary_edge.next_edge.next_edge.next_edge.edge_id == ((5, 1), (2,3))  #type: ignore
  
  def test_inner_boundary_connectivity_face_2(self, polygon_a, polygon_b) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)
    mesh.add_polygon(polygon_b)
    
    # Verify that the face ID is the same as the dict key.
    face_2: MeshFace = mesh._faces[2] 
    assert face_2.face_id == 2

    # Verify that the inner half-edges are correct for Face 2.
    assert face_2.boundary_edge.edge_indicator == 2                                         #type: ignore
    assert face_2.boundary_edge.edge_id == ((9,3), (6,6))                                   #type: ignore
    assert face_2.boundary_edge.next_edge.edge_indicator == 5                               #type: ignore
    assert face_2.boundary_edge.next_edge.edge_id == ((6, 6), (10,7))                       #type: ignore
    assert face_2.boundary_edge.next_edge.next_edge.edge_indicator == 6                     #type: ignore
    assert face_2.boundary_edge.next_edge.next_edge.edge_id == ((10,7), (13, 4))            #type: ignore
    assert face_2.boundary_edge.next_edge.next_edge.next_edge.edge_indicator == 7           #type: ignore
    assert face_2.boundary_edge.next_edge.next_edge.next_edge.edge_id == ((13, 4), (9, 3))  #type: ignore

  def test_outer_boundary_connectivity_for_single_face(self, polygon_a) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)

    face_1: MeshFace = mesh._faces[1] 
    starting_outer_edge: MeshHalfEdge = face_1.boundary_edge.pair_edge #type: ignore
    assert starting_outer_edge.edge_indicator == 1
    assert starting_outer_edge.edge_id == ((6, 6), (2, 3))
    assert starting_outer_edge.face is None

    # There should 4 outer edges and all outer edges should not have an associated face.
    # The outer boundary should be: 
    # Edge 1 -> Edge 4 -> Edge 3 -> Edge 2
    edge_visit_order = []
    collect_edge_indicators = lambda e: edge_visit_order.append(e.edge_indicator)

    edge_counter = CounterBuilder.count_up_from_zero()
    traverse_edges_by_next(
      starting_outer_edge, 
      max_traversals=10, 
      actions=[assert_edge_with_no_face, collect_edge_indicators], 
      counter = edge_counter
    )
    assert edge_counter.value() == 4
    assert edge_visit_order == [1, 4, 3, 2]

  def test_traversing_around_vertices_for_single_face(self, polygon_a) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)
    
    # Traverse the edge around V1.
    edge_order = []
    collect_outbound_edges = lambda e: edge_order.append(e.edge_indicator)
    
    edge_counter = CounterBuilder.count_up_from_zero()
    traverse_edges_around_vertex(
      vertex = mesh.vertex_at(Coordinate(2, 3)),
      max_traversals = 10,
      actions= [collect_outbound_edges],
      counter = edge_counter
    )
    assert edge_counter.value() == 2
    assert edge_order == [1, 4]

    # Traverse the edge around V2.
    edge_order.clear()
    edge_counter.reset()
    traverse_edges_around_vertex(
      vertex = mesh.vertex_at(Coordinate(6, 6)),
      max_traversals = 10,
      actions= [collect_outbound_edges],
      counter = edge_counter
    )
    assert edge_counter.value() == 2
    assert edge_order == [2, 1]

    # Traverse the edge around V3.
    edge_order.clear()
    edge_counter.reset()
    traverse_edges_around_vertex(
      vertex = mesh.vertex_at(Coordinate(9, 3)),
      max_traversals = 10,
      actions= [collect_outbound_edges],
      counter = edge_counter
    )
    assert edge_counter.value() == 2
    assert edge_order == [3, 2]

    # Traverse the edge around V4.
    edge_order.clear()
    edge_counter.reset()
    traverse_edges_around_vertex(
      vertex = mesh.vertex_at(Coordinate(5, 1)),
      max_traversals = 10,
      actions= [collect_outbound_edges],
      counter = edge_counter
    )
    assert edge_counter.value() == 2
    assert edge_order == [4, 3]


  def test_outer_boundary_connectivity_for_two_faces(self, polygon_a, polygon_b) -> None:
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)
    mesh.add_polygon(polygon_b)

    face_1: MeshFace = mesh._faces[1] 
    starting_outer_edge: MeshHalfEdge = face_1.boundary_edge.pair_edge #type: ignore
    assert starting_outer_edge.edge_indicator == 1
    assert starting_outer_edge.edge_id == ((6, 6), (2, 3))
    assert starting_outer_edge.face is None

    # There should 6 outer edges and all outer edges should not have an associated face.
    # The outer boundary should be: 
    # Edge 1 -> Edge 4 -> Edge 3 -> Edge 7 -> Edge 6 -> Edge 5
    edge_visit_order = []
    collect_edge_indicators = lambda e: edge_visit_order.append(e.edge_indicator)

    edge_counter = CounterBuilder.count_up_from_zero()
    traverse_edges_by_next(
      starting_outer_edge, 
      max_traversals=10, 
      actions=[assert_edge_with_no_face, collect_edge_indicators], 
      counter = edge_counter
    )
    assert edge_counter.value() == 6
    assert edge_visit_order == [1, 4, 3, 7, 6, 5]
  
def traverse_edges_by_next(
  starting_edge: MeshHalfEdge, 
  max_traversals: int, 
  actions: list[Callable[[MeshHalfEdge], None]],
  counter: Counter
) -> None:
  """Given a half-edge, follows the next points until a loop is encountered."""
  first_edge: MeshHalfEdge = starting_edge
  current_edge: MeshHalfEdge | None = starting_edge
  while True:
    counter.increment()
    for action in actions:
      action(current_edge)
    current_edge = current_edge.next_edge
    if current_edge is None or current_edge == first_edge or counter.value() > max_traversals:
      break

def assert_edge_with_no_face(edge: MeshHalfEdge): 
  assert edge.face == None

def traverse_edges_around_vertex(
  vertex: MeshVertex, 
  max_traversals: int, 
  actions: list[Callable[[MeshHalfEdge], None]],
  counter: Counter
) -> None:
  """Given a mesh vertex, visit all of the edges that start from the vertex."""
  if vertex.edge is None:
    raise MeshException("Cannot traverse around a vertex that has no associated edge")
  
  starting_edge = vertex.edge
  current_edge: MeshHalfEdge | None = starting_edge
  while True:
    counter.increment()
    for action in actions:
      action(current_edge)
    current_edge = current_edge.pair_edge.next_edge #type: ignore
    if current_edge is None or current_edge == starting_edge or counter.value() > max_traversals:
      break

