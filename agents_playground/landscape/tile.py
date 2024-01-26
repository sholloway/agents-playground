from __future__ import annotations

from dataclasses import dataclass
from enum import auto, Enum
from typing import Dict, List, NamedTuple

from agents_playground.fp import Maybe
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.vertex import Vertex3d

class TileType(Enum):
  Square = auto()

class TileDirection(Enum):
  North = auto()
  South = auto()
  East  = auto()
  West  = auto()

class TileCoordinate(NamedTuple):
  ...
  # perhaps this should be somewhere else.

# Note: Perhaps Tile should be in the spatial package.
# I could expand the spatial.types.Coordinate to be in 3D.

@dataclass
class Tile:
  location: TileCoordinate                            # In the landscape coordinate system. 
  transformation: Maybe[Matrix4x4]                    # The information for where the tile is in world space. This is not in the scene file, but calculated once when loaded.
  edges: List[Edge3d]                                 # In the landscape coordinate system. 
  vertices: List[Vertex3d]                            # Clockwise winding 
  neighbors: Dict[TileDirection, Tile]                # Direction for a tile is N/S/E/W, it would be different for a triangle or hexagon. 
  state: Maybe[TileState]                             # An optional member that enables storing state in a table. 
  state_transition_map: Maybe[TileStateTransitionMap] # If there is a state, then there needs to be a transition map to enable FSM behavior.
  system: Maybe[TileSystem]                           # An optional member to enable having logic associated with the tile.
  material: MaterialId                                # A related material to render the tile as. 
  texture: Maybe[TextureId]                           # An optional texture to project onto the tile. 