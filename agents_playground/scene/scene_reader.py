from math import radians
from typing import Dict, List, Tuple

from deprecated import deprecated
from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.fp import Nothing
from agents_playground.scene import Scene, Transformation
from agents_playground.scene.scene_characteristics import SceneCharacteristics
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.landscape.constants import STANDARD_GRAVITY_IN_METRIC
from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile, TileCubicPlacement, TileDirection
from agents_playground.spatial.landscape.types import LandscapeGravityUOM, LandscapeMeshType
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector.vector3d import Vector3d
from agents_playground.uom import LengthUOM, SystemOfMeasurement

def t(*args) -> Tile:
  return Tile(location=Coordinate(*args), direction=TileDirection.NORMAL)

@deprecated(reason='Replaced by agents_playground.loaders.scene_loader.SceneLoader')
class SceneReader:
  """Currently a stub for reading a Scene definition file."""
  def load(self, path) -> Scene:
    camera: Camera = Camera3d.look_at(
      position     = Vector3d(2.0, 2.0, 3.0),
      target       = Vector3d(0.0, 0.0, 0.0),
      near_plane   = 0.1,
      far_plane    = 100.0,
      vertical_fov = 72.0,
      aspect_ratio = "16:9"
    )

    lc = LandscapeCharacteristics(
      mesh_type   = LandscapeMeshType.SQUARE_TILE,
      landscape_uom_system = SystemOfMeasurement.METRIC, 
      tile_size_uom = LengthUOM.METER,
      tile_width  = 1.0,
      tile_height = 1.0,
      tile_depth  = 1.0,
    )

    physicality = LandscapePhysicality(
      gravity_uom = LandscapeGravityUOM.METERS_PER_SECOND_SQUARED,
      gravity_strength = STANDARD_GRAVITY_IN_METRIC
    )

    # A list of tile coordinates in the form (x,y,z,side)
    # TODO: Don't allow specifying the same tile multiple times.
    # Use Cases 
    tile_locations: List[Tuple[int, int, int, TileCubicPlacement, TileDirection]] = [
      # Create a Cube
      # (0, 0, 0, TileCubicPlacement.BOTTOM, TileDirection.NORMAL),
      # (0, 0, 0, TileCubicPlacement.TOP,    TileDirection.NORMAL),
      # (0, 0, 0, TileCubicPlacement.FRONT,  TileDirection.NORMAL),
      # (0, 0, 0, TileCubicPlacement.BACK,   TileDirection.NORMAL),
      # (0, 0, 0, TileCubicPlacement.LEFT,   TileDirection.NORMAL),
      # (0, 0, 0, TileCubicPlacement.RIGHT,  TileDirection.NORMAL),


      # Base floor. These All Work.
      # (0, 0, 0, TileCubicPlacement.BOTTOM,  TileDirection.NORMAL),
      # (1, 0, 0, TileCubicPlacement.BOTTOM,  TileDirection.NORMAL),
      # (2, 0, 0, TileCubicPlacement.BOTTOM,  TileDirection.NORMAL),
      # (2, 0, 1, TileCubicPlacement.BOTTOM,  TileDirection.NORMAL),
      # (2, 0, 2, TileCubicPlacement.BOTTOM,  TileDirection.NORMAL),
      # (3, 0, 0, TileCubicPlacement.BOTTOM,  TileDirection.NORMAL),
      # (4, 0, 0, TileCubicPlacement.BOTTOM,  TileDirection.NORMAL),
      # (5, 0, 0, TileCubicPlacement.BOTTOM,  TileDirection.NORMAL),

      
      # Add some diagonals.
      (0, 0, 0, TileCubicPlacement.BOTTOM,  TileDirection.NORMAL),
      (0, 0, 1, TileCubicPlacement.FB_UP,   TileDirection.NORMAL),
      (0, 0, 2, TileCubicPlacement.FB_DOWN, TileDirection.NORMAL),
      (1, 0, 0, TileCubicPlacement.LR_UP,   TileDirection.NORMAL),
      (-1, 0, 0, TileCubicPlacement.LR_DOWN,   TileDirection.NORMAL),
      (0, 0, -1, TileCubicPlacement.FB_LR,  TileDirection.NORMAL),
      (0, 0, -2, TileCubicPlacement.FB_RL,  TileDirection.NORMAL),
    ]


    
    tiles: List[Tile] = [Tile(location = Coordinate(*t[:-1]), direction=t[-1]) for t in tile_locations]

    landscape = Landscape(
      file_characteristics = Nothing(),
      characteristics = lc,
      physicality = physicality,
      custom_attributes = {},
      tiles = { t.location : t for t in tiles} # Build a dict with the tile location as the key.
    )

    landscape_transformation = Transformation(
      translation = Vector3d(0, 0, 0),
      rotation = Vector3d(0, 0, 0),
      scale = Vector3d(1, 1, 1)
    )
    
    return Scene(
      file_characteristics = Nothing(),
      characteristics = SceneCharacteristics(
        scene_uom_system = SystemOfMeasurement.METRIC,
        scene_distance_uom = LengthUOM.CENTIMETER
      ),
      camera = camera,
      landscape = landscape,
      landscape_transformation = landscape_transformation
    )