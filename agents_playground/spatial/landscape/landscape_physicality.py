from dataclasses import dataclass

from agents_playground.spatial.landscape.types import LandscapeGravityUOM

@dataclass
class LandscapePhysicality:
  """
  The physical aspects of the landscape.
  """
  gravity_uom: LandscapeGravityUOM 
  gravity_strength: float

  def __post_init__(self) -> None:
    if isinstance(self.gravity_uom, str):
      self.gravity_uom = LandscapeGravityUOM(self.gravity_uom)