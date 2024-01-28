from dataclasses import dataclass

from agents_playground.spatial.landscape.types import LandscapeMeshType, LandscapeTileUOM, TileDimension
from agents_playground.uom import LengthUOM, SystemOfMeasurement

@dataclass
class LandscapeCharacteristics:
  mesh_type:  LandscapeMeshType
  landscape_uom_system: SystemOfMeasurement 
  tile_size_uom: LengthUOM
  tile_width: TileDimension
  tile_height: TileDimension
  wall_height: TileDimension 