from math import radians
from typing import Dict, List, Tuple
from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.fp import Nothing
from agents_playground.scene import Scene
from agents_playground.scene.scene_characteristics import SceneCharacteristics
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.landscape.constants import STANDARD_GRAVITY_IN_METRIC
from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile, TileCubicPlacement
from agents_playground.spatial.landscape.types import LandscapeGravityUOM, LandscapeMeshType
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector.vector3d import Vector3d
from agents_playground.uom import LengthUOM, SystemOfMeasurement

def t(x,y,z, s) -> Tile:
  return Tile(location=Coordinate(x,y,z,z))

class SceneReader:
  """Currently a stub for reading a Scene definition file."""
  def load(self, path) -> Scene:
    aspect_ratio: float = 800.0/894.0 # Placeholder for right now.
    
    camera: Camera = Camera3d.look_at(
      position = Vector3d(3.0, 2.0, -2.0),
      target   = Vector3d(0.0, 0.0, 0.0),
      projection_matrix = Matrix4x4.perspective(
        aspect_ratio= aspect_ratio, 
        v_fov = radians(72.0), 
        near = 0.01, 
        far = 100.0
      )
    )

    lc = LandscapeCharacteristics(
      mesh_type   = LandscapeMeshType.SquareTile,
      landscape_uom_system = SystemOfMeasurement.METRIC, 
      tile_size_uom = LengthUOM.METER,
      tile_width  = 1.0,
      tile_height = 1.0,
      tile_depth  = 1.0,
    )

    physicality = LandscapePhysicality(
      gravity_uom = LandscapeGravityUOM.MetersPerSecondSquared,
      gravity = STANDARD_GRAVITY_IN_METRIC
    )

    # A list of tile coordinates in the form (x,y,z,side)
    # TODO: Don't allow specifying the same tile multiple times.
    # Use Cases 
    tile_locations: List[Tuple[int,...]] = [
      # Create a Cube
      (0, 0, 0, TileCubicPlacement.BOTTOM),
      (0, 0, 0, TileCubicPlacement.TOP),
      (0, 0, 0, TileCubicPlacement.FRONT),
      (0, 0, 0, TileCubicPlacement.BACK),
      (0, 0, 0, TileCubicPlacement.LEFT),
      (0, 0, 0, TileCubicPlacement.RIGHT),


      # Base floor. These All Work.
      # (0, 0, 0, TileCubicPlacement.BOTTOM),
      # (1, 0, 0, TileCubicPlacement.BOTTOM),
      # (2, 0, 0, TileCubicPlacement.BOTTOM),
      # (2, 0, 1, TileCubicPlacement.BOTTOM),
      # (2, 0, 2, TileCubicPlacement.BOTTOM),
      # (3, 0, 0, TileCubicPlacement.BOTTOM),
      # (4, 0, 0, TileCubicPlacement.BOTTOM),
      # (5, 0, 0, TileCubicPlacement.BOTTOM),

      #Put some walls up
      # (2, 0, 1, TileCubicPlacement.BACK), Failing.

      # Add some diagonals.
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
      file_characteristics = Nothing(),
      characteristics = SceneCharacteristics(
        scene_uom_system = SystemOfMeasurement.METRIC,
        scene_distance_uom = LengthUOM.CENTIMETER
      ),
      camera = camera,
      landscape = landscape,
      landscape_location = Vector3d(0,0,0),
      landscape_scale = Vector3d(1,1,1),
      landscape_rotation = Vector3d(0,0,0)
    )