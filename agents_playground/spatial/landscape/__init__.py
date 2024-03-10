
from dataclasses import dataclass
from typing import Any, cast
from agents_playground.fp import Maybe, Nothing, Something, wrap_field_as_maybe
from agents_playground.spatial.coordinate import Coordinate, CoordinateComponentType

from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_file_characteristics import LandscapeFileCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile, TileCubicPlacement, TileCubicVerticesPlacement
from agents_playground.spatial.vector.vector import Vector
from . import *

@dataclass
class Landscape:
  """
  A landscape is a collection of tiles organized in a multi-dimensional
  axis-aligned lattice. 
  
  The lattice is composed of uniform empty volumes. To get started, 
  a volume is a uniform cube. A physical landscape can be defined 
  by assigning tiles to the various sides of a block.

  The coordinate system of how tiles fit in the lattice is
  Tile Location = (X, Y, Z, S)
  Where:
    X: Is the unit distance along the X-axis to the volume's centroid.
    Y: Is the unit distance along the Y-axis to the volume's centroid.
    Z: Is the unit distance along the Z-axis to the volume's centroid.
    S: Is the respective side of the volume.

  Cube sides are in relation to the cube's centroid. 
  """
  file_characteristics: Maybe[LandscapeFileCharacteristics]
  characteristics: LandscapeCharacteristics
  physicality: LandscapePhysicality
  custom_attributes: dict[str, Any] # Placeholder for simulation specific attributes. 
  tiles: dict[Coordinate, Tile] 
  debug: Any

  def __post_init__(self) -> None:
    """
    A landscape is loaded from a JSON file. When that happens a dict[str, Any] is 
    passed into a Landscape instance like Landscape(**json_obj). To handle this correctly,
    The various landscape members need to be set correctly.
    """
    # If being set from JSON, self.file_characteristics will be a dict.
    # This needs to be converted to a LandscapeFileCharacteristics data class wrapped in a Maybe.
    wrap_field_as_maybe(self, 'file_characteristics', lambda f: LandscapeFileCharacteristics(**f))
    
    # If being set from JSON, self.characteristics will be a dict.
    # Set to an instance of LandscapeCharacteristics.
    if isinstance(self.characteristics, dict):
      self.characteristics = LandscapeCharacteristics(**self.characteristics)
    
    if isinstance(self.physicality, dict):
      self.physicality = LandscapePhysicality(**self.physicality)

    # If being set from JSON, then self.tiles will be a list of dict[str, Any]
    # Convert this to dict[Coordinate, Tile]
    if isinstance(self.tiles, list):
      tile_placements: list[list[int]] = cast(list[list[int]], self.tiles)
      self.tiles: dict[Coordinate, Tile] = {}
      tile_placement: list[int]

      for tile_placement in tile_placements:
        tile = Tile(location=Coordinate(*tile_placement))
        self.tiles[tile.location] = tile    

def cubic_tile_to_vertices(tile: Tile, lc: LandscapeCharacteristics) -> list[Coordinate]:
  """
  Converts a tile to the vertices that define it.
  """
  # 1. Determine the vertices by the tile used on a unit cube.
  tile_orientation: int  = cast(int, tile.location[3])
  vertex_unit_vectors: tuple[Vector, ...] = TileCubicVerticesPlacement[TileCubicPlacement(tile_orientation)]

  # 2. Scale and translate the vertices to be the size specified by the landscape characteristics.
  x_offset = lc.tile_width * cast(int,tile.location[0])
  y_offset = lc.tile_height * cast(int,tile.location[1])
  z_offset = lc.tile_depth * cast(int,tile.location[2])

  scaled_vertices: list[Coordinate] = \
    [ Coordinate(v.i*lc.tile_width + x_offset, v.j*lc.tile_height + y_offset, v.k* lc.tile_depth + z_offset) 
      for v in vertex_unit_vectors ]

  # 4. Return the vertices. 
  return scaled_vertices