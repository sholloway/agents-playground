from dataclasses import dataclass

from agents_playground.uom import LengthUOM, SystemOfMeasurement

@dataclass
class SceneCharacteristics:
  scene_uom_system: SystemOfMeasurement 
  scene_distance_uom: LengthUOM # Defines what one "unit" in the scene is (e.g 1 inch, 1 foot, 1 meter, etc...)