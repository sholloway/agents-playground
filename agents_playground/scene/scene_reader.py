from math import radians
from typing import Dict, List, Tuple
from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.fp import Nothing
from agents_playground.scene import Scene
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.landscape.constants import STANDARD_GRAVITY_IN_METRIC
from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile, TileCubicPlacement
from agents_playground.spatial.landscape.types import LandscapeGravityUOM, LandscapeMeshType, LandscapeTileUOM
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector.vector3d import Vector3d

def t(x,y,z, s) -> Tile:
  return Tile(location=Coordinate(x,y,z,z))

class SceneReader:
  """Currently a stub for reading a Scene definition file."""
  def load(self, path) -> Scene:
    aspect_ratio: float = 800.0/894.0 # Placeholder for right now.
    
    camera: Camera = Camera3d.look_at(
      position = Vector3d(3, 2, 4),
      target   = Vector3d(0, 0, 0),
      projection_matrix = Matrix4x4.perspective(
        aspect_ratio= aspect_ratio, 
        v_fov = radians(72.0), 
        near = 0.1, 
        far = 100.0
      )
    )

    lc = LandscapeCharacteristics(
      mesh_type   = LandscapeMeshType.SquareTile,
      tile_uom    = LandscapeTileUOM.Meters, 
      tile_width  = 1,
      tile_height = 1,
      wall_height = 1,
    )

    physicality = LandscapePhysicality(
      gravity_uom = LandscapeGravityUOM.MetersPerSecondSquared,
      gravity = STANDARD_GRAVITY_IN_METRIC
    )

    # A list of tile coordinates in the form (x,y,z,side)
    tile_locations: List[Tuple[int,...]] = [
      (0, 0, 0, TileCubicPlacement.Bottom),
      (1, 0, 0, TileCubicPlacement.Bottom),
      (2, 0, 0, TileCubicPlacement.Bottom),
      (3, 0, 0, TileCubicPlacement.Bottom),
      (4, 0, 0, TileCubicPlacement.Bottom),
      (5, 0, 0, TileCubicPlacement.Bottom),
    ]
    
    tiles: List[Tile] = [Tile(Coordinate(*t)) for t in tile_locations]

    landscape = Landscape(
      file_characteristics = Nothing(),
      characteristics = lc,
      physicality = physicality,
      custom_attributes = {},
      tiles = { t.location : t for t in tiles} # Build a dict with the tile location as the key.
    )
    
    return Scene(
      camera = camera,
      landscape = landscape
    )