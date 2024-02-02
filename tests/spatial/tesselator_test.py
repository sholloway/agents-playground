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

  def test_construct_landscape_mesh(self, linear_landscape_strip: Landscape) -> None:
    assert len(linear_landscape_strip.tiles) == 6
    mesh: Mesh = Mesh(winding=MeshWindingDirection.CW)

    for tile in linear_landscape_strip.tiles.values():
      tile_vertices = cubic_tile_to_vertices(tile, linear_landscape_strip.characteristics)
      mesh.add_polygon(tile_vertices)

    

