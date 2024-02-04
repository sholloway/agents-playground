import pytest

from agents_playground.fp import Nothing
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.landscape.constants import STANDARD_GRAVITY_IN_METRIC
from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile, TileCubicPlacement, TileCubicVerticesPlacement
from agents_playground.spatial.landscape.types import LandscapeGravityUOM, LandscapeMeshType
from agents_playground.spatial.mesh.tesselator import Mesh, MeshWindingDirection
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

    # Inspect the edge between vertices 2 and 3. Adding the second polygon should have set the face on 
    # the external edge between vert 2 and 3 to Face ID #2.
    half_edge_between_verts_2_3 = mesh.half_edge_between(Coordinate(9, 3), Coordinate(6, 6))
    assert half_edge_between_verts_2_3 is not None 
    assert half_edge_between_verts_2_3.edge_indicator == 2
    assert half_edge_between_verts_2_3.face.face_id == 2    #type: ignore

    