from dataclasses import dataclass

from agents_playground.spatial.landscape.types import LandscapeMeshType, LandscapeTileUOM, TileDimension

@dataclass
class LandscapeCharacteristics:
  mesh_type:  LandscapeMeshType
  tile_uom: LandscapeTileUOM 
  tile_width: TileDimension
  tile_height: TileDimension
  wall_height: TileDimension 