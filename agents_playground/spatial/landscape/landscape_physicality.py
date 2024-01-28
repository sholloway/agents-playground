from dataclasses import dataclass

from agents_playground.spatial.landscape.types import LandscapeGravityUOM

@dataclass
class LandscapePhysicality:
  gravity_uom: LandscapeGravityUOM 
  gravity: float