from __future__ import annotations

from dataclasses import dataclass
from enum import auto, Enum, IntEnum

from typing import Dict, List, NamedTuple

from agents_playground.fp import Maybe
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vector.vector3d import Vector3d
from agents_playground.spatial.vertex import Vertex3d

class TileType(Enum):
  Square = auto()

class TileCubicPlacement(IntEnum):
  """
  Given a tile placed on an axis aligned cube, the TileCubicPlacement
  specifies which face of the volume the tile is on.

  Front/Back are on the X-axis.
  Top/Bottom are on the Y-axis.
  Left/Right are on the Z-axis.
  """
  # The Cube Sides
  FRONT  = auto()
  BACK   = auto()
  TOP    = auto()
  BOTTOM = auto()
  RIGHT  = auto()
  LEFT   = auto()

  # The Cube Diagonals. These are used to create and walls at angles.
  # Diagonals are formed by defining a tile between opposing edges.
  # For example FB_UP is connection the the Front Face to the Back Face 
  # By a Tile from the lower edge on the front face to the upper edge on the back face.
  FB_UP   = auto() # Front to Back, Lower Front Edge to Top Bottom Edge
  FB_DOWN = auto() # Front to Back, Top Front Edge to Bottom Lower Edge 
  LR_UP   = auto() # Left to Right, Lower Left Edge to Top Right Edge
  LR_DOWN = auto() # Left to Right, Top Left Edge to Bottom Right Edge 
  FB_LR   = auto() # Front to Back, Front Left Vertical Edge to Back Right Vertical Edge
  FB_RL   = auto() # Front to Back, Front Right Vertical Edge to Back Left Vertical Edge.


"""
For a cube with it's front left lower corner at the origin (0,0,0)...
The coordinates of the 8 vertices can be determined with unit vectors. 
As such, Tiles can leverage a lookup table to determine vertex placement.

Y
^      H           E
|       O-----------O
|      /           /|
|     /         A / |
|  D O----------O   |
|    |          |   O F
|    |          |  /
|    |          | /
|    O----------O         
|    C          B
|
-------------------------> X
"""
class CubicVertexUnitVectors:
  A = Vector3d(1, 1, 0)
  B = Vector3d(1, 0, 0)
  C = Vector3d(0, 0, 0)
  D = Vector3d(0, 1, 0)
  E = Vector3d(1, 1, 1)
  F = Vector3d(1, 0, 1)
  G = Vector3d(0, 0, 1)
  H = Vector3d(0, 1, 1)

TileCubicVerticesPlacement: dict[TileCubicPlacement, tuple[Vector, ...]] = {
  TileCubicPlacement.BOTTOM: (CubicVertexUnitVectors.F, CubicVertexUnitVectors.B, CubicVertexUnitVectors.C, CubicVertexUnitVectors.G),
  TileCubicPlacement.FRONT:  (CubicVertexUnitVectors.D, CubicVertexUnitVectors.C, CubicVertexUnitVectors.B, CubicVertexUnitVectors.A),
  TileCubicPlacement.TOP:    (CubicVertexUnitVectors.H, CubicVertexUnitVectors.D, CubicVertexUnitVectors.A, CubicVertexUnitVectors.E),
  TileCubicPlacement.LEFT:   (CubicVertexUnitVectors.G, CubicVertexUnitVectors.C, CubicVertexUnitVectors.D, CubicVertexUnitVectors.H),
  TileCubicPlacement.BACK:   (CubicVertexUnitVectors.E, CubicVertexUnitVectors.F, CubicVertexUnitVectors.G, CubicVertexUnitVectors.H),
  TileCubicPlacement.RIGHT:  (CubicVertexUnitVectors.B, CubicVertexUnitVectors.F, CubicVertexUnitVectors.E, CubicVertexUnitVectors.A),
  
  # Ramps
  TileCubicPlacement.FB_UP:   (CubicVertexUnitVectors.B, CubicVertexUnitVectors.C, CubicVertexUnitVectors.H, CubicVertexUnitVectors.E),
  TileCubicPlacement.FB_DOWN: (CubicVertexUnitVectors.A, CubicVertexUnitVectors.D, CubicVertexUnitVectors.G, CubicVertexUnitVectors.F),
  TileCubicPlacement.LR_UP:   (CubicVertexUnitVectors.C, CubicVertexUnitVectors.G, CubicVertexUnitVectors.E, CubicVertexUnitVectors.A),
  TileCubicPlacement.LR_DOWN: (CubicVertexUnitVectors.D, CubicVertexUnitVectors.H, CubicVertexUnitVectors.F, CubicVertexUnitVectors.B),
  
  # Diagonal Walls
  TileCubicPlacement.FB_LR: (CubicVertexUnitVectors.C, CubicVertexUnitVectors.D, CubicVertexUnitVectors.E, CubicVertexUnitVectors.F), 
  TileCubicPlacement.FB_RL: (CubicVertexUnitVectors.B, CubicVertexUnitVectors.A, CubicVertexUnitVectors.H, CubicVertexUnitVectors.G)
}

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

class TileDirection(IntEnum):
  NORMAL  = 1
  REVERSE = -1

@dataclass
class Tile:
  location: Coordinate                                  # In the landscape coordinate system. 
  direction: TileDirection = TileDirection.NORMAL

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