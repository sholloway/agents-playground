import datetime
from enum import auto, Enum, StrEnum


class LandscapeMeshType(StrEnum):
    SQUARE_TILE = "SQUARE_TILE"


class LandscapeTileUOM(StrEnum):
    FEET = "FEET"
    METERS = "METERS"


class LandscapeGravityUOM(StrEnum):
    METERS_PER_SECOND_SQUARED = (
        "METERS_PER_SECOND_SQUARED"  # The Standard Gravity Constant
    )
    FEET_PER_SECOND_SQUARED = "FEET_PER_SECOND_SQUARED"


"""
TileDimension represents a span of space in a landscape's coordinate system. 
Intended to be used with the LandscapeTileUom.
If the Landscape tile_uom is LandscapeTileUom.Meters then a 
value of 1 for tile_width for example means that all tiles are 
1 meter wide.
"""
TileDimension = int | float
