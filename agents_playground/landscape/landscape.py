import datetime 
from dataclasses import dataclass
from enum import auto, Enum
from typing import Any, Dict

from agents_playground.fp import Maybe
from agents_playground.spatial.types import Coordinate

class LandscapeMeshType(Enum):
  SquareTile = auto()

class LandscapeTileUOM(Enum):
  Feet = auto()
  Meters = auto()

class LandscapeGravityUOM:
  MetersPerSecondSquared = auto() # The Standard Gravity Constant

STANDARD_GRAVITY = 9.80665

"""
TileDimension represents a span of space in a landscape's coordinate system. 
Intended to be used with the LandscapeTileUom.
If the Landscape tile_uom is LandscapeTileUom.Meters then a 
value of 1 for tile_width for example means that all tiles are 
1 meter wide.
"""
TileDimension = int 

# This should be moved to a package with a wider scope. 
DateTime = datetime.datetime 

@dataclass
class LandscapeFileCharacteristics:
  author: Maybe[str] # Can be any string but intended to be First Name Last Name 
  license: Maybe[str] # The license type for this attribute. 
  contact: Maybe[str] # Contact information. Could be anything.
  creation_time: Maybe[DateTime] # 2024-01-21 hh:mm:ss
  updated_time: Maybe[DateTime] #YYYY-MM-DD hh:mm:ss

@dataclass
class LandscapeCharacteristics:
  mesh_type:  LandscapeMeshType
  tile_uom: LandscapeTileUOM 
  tile_width: TileDimension
  tile_height: TileDimension
  wall_height: TileDimension 

@dataclass
class LandscapePhysicality:
  gravity_uom: LandscapeGravityUOM 
  gravity: float

@dataclass
class Landscape:
  characteristics: LandscapeCharacteristics
  physicality: LandscapePhysicality
  custom_attributes: Dict[str, Any] # Placeholder for simulation specific attributes. 

  # Option 1: Store tiles in a dict by their 3d coordinates. 
  # Option 2: Use a compact data structure to minimize vertex/edges duplication.
  tiles: Dict[Coordinate, Tile] 