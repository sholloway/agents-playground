from __future__ import annotations

from dataclasses import dataclass
from enum import auto, Enum
from typing import Dict, List, NamedTuple

from agents_playground.fp import Maybe
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.vertex import Vertex3d

class TileType(Enum):
  Square = auto()

class TileDirection(Enum):
  North = auto()
  South = auto()
  East  = auto()
  West  = auto()


"""
Implementation Thoughts
- For members that are optional, a Nothing() instance is 56 bytes.
- The Tile class may be a good fit for using __slots__ to reduce memory overhead.
  https://wiki.python.org/moin/UsingSlots
- Polygon may also be a good fit for using __slots__.
- Consider that the Tile class should only contain data in the landscape coordinate system.
  A compute shader should generate the triangles and vertices locations in world space.

Flows
- Editor -> File 
- File -> Running Sim
"""

@dataclass
class Tile:
  location: Coordinate                                  # In the landscape coordinate system. 
  # transformation: Maybe[Matrix]                       # The information for where the tile is in world space. This is not in the scene file, but calculated once when loaded.
  # edges: List[Edge3d]                                 # In the landscape coordinate system. 
  # vertices: List[Vertex3d]                            # Clockwise winding 
  # neighbors: Dict[TileDirection, Tile]                # Direction for a tile is N/S/E/W, it would be different for a triangle or hexagon. 
  
  # Ideas for after the basic rendering path is done
  # state: Maybe[TileState]                             # An optional member that enables storing state in a table. 
  # state_transition_map: Maybe[TileStateTransitionMap] # If there is a state, then there needs to be a transition map to enable FSM behavior.
  # system: Maybe[TileSystem]                           # An optional member to enable having logic associated with the tile.
  # material: MaterialId                                # A related material to render the tile as. 
  # texture: Maybe[TextureId]                           # An optional texture to project onto the tile. 