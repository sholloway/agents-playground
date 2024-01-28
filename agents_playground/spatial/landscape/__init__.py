
from dataclasses import dataclass
from typing import Any, Dict
from agents_playground.fp import Maybe
from agents_playground.spatial.coordinate import Coordinate

from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_file_characteristics import LandscapeFileCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile
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