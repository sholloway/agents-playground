from dataclasses import dataclass

from agents_playground.spatial.landscape.types import (
    LandscapeMeshType,
    LandscapeTileUOM,
    TileDimension,
)
from agents_playground.uom import LengthUOM, SystemOfMeasurement


@dataclass
class LandscapeCharacteristics:
    """
    The defining characteristics of a landscape.
    Specifies the shape of the lattice.
    """

    mesh_type: LandscapeMeshType
    landscape_uom_system: SystemOfMeasurement
    tile_size_uom: LengthUOM
    tile_width: TileDimension  # X-axis
    tile_height: TileDimension  # Y-axis
    tile_depth: TileDimension  # Z-Axis

    def __post_init__(self) -> None:
        if isinstance(self.mesh_type, str):
            self.mesh_type = LandscapeMeshType(self.mesh_type)

        if isinstance(self.landscape_uom_system, str):
            self.landscape_uom_system = SystemOfMeasurement(self.landscape_uom_system)

        if isinstance(self.tile_size_uom, str):
            self.tile_size_uom = LengthUOM(self.tile_size_uom)
