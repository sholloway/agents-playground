
from dataclasses import dataclass
from typing import Any, Dict
from agents_playground.fp import Maybe
from agents_playground.spatial.coordinate import Coordinate

from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_file_characteristics import LandscapeFileCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile, TileCubicVerticesPlacement
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
  custom_attributes: Dict[str, Any] # Placeholder for simulation specific attributes. 
  tiles: Dict[Coordinate, Tile] 

def cubic_tile_to_vertices(tile: Tile, lc: LandscapeCharacteristics) -> list[Coordinate]:
  """
  Converts a tile to the vertices that define it.
  """
  # 1. Determine the vertices by the tile used on a unit cube.
  vertex_unit_vectors: tuple[Vector, ...] = TileCubicVerticesPlacement[tile.location[3]]

  # 2. Scale and translate the vertices to be the size specified by the landscape characteristics.
  x_offset = lc.tile_width * tile.location[0]
  y_offset = lc.tile_height * tile.location[1]
  z_offset = lc.tile_depth * tile.location[2]

  scaled_vertices: list[Coordinate] = \
    [ Coordinate(v.i*lc.tile_width + x_offset, v.j*lc.tile_height + y_offset, v.k* lc.tile_depth + z_offset) 
      for v in vertex_unit_vectors ]

  # 4. Return the vertices. 
  return scaled_vertices