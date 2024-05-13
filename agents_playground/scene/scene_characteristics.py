from dataclasses import dataclass

from agents_playground.uom import LengthUOM, SystemOfMeasurement

@dataclass
class SceneCharacteristics:
  name: str
  title: str
  description: str 
  scene_uom_system: SystemOfMeasurement 
  scene_distance_uom: LengthUOM # Defines what one "unit" in the scene is (e.g 1 inch, 1 foot, 1 meter, etc...)

  def __post_init__(self) -> None:
    if isinstance(self.scene_uom_system, str):
      self.scene_uom_system = SystemOfMeasurement(self.scene_uom_system)
    
    if isinstance(self.scene_distance_uom, str):
      self.scene_distance_uom = LengthUOM(self.scene_distance_uom)