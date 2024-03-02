from dataclasses import dataclass

from agents_playground.spatial.landscape.types import LandscapeGravityUOM

@dataclass
class LandscapePhysicality:
  """
  The physical aspects of the landscape.
  """
  gravity_uom: LandscapeGravityUOM 
  gravity_strength: float