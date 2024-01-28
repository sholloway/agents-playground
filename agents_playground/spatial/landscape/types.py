import datetime
from enum import Enum, auto

class LandscapeMeshType(Enum):
  SquareTile = auto()

class LandscapeTileUOM(Enum):
  Feet = auto()
  Meters = auto()

class LandscapeGravityUOM(Enum):
  MetersPerSecondSquared = auto() # The Standard Gravity Constant

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