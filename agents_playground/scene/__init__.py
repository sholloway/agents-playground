from dataclasses import dataclass

from agents_playground.cameras.camera import Camera
from agents_playground.fp import Maybe
from agents_playground.scene.scene_characteristics import SceneCharacteristics
from agents_playground.scene.scene_file_characteristics import SceneFileCharacteristics
from agents_playground.spatial.landscape import Landscape

@dataclass
class Scene:
  camera: Camera
  landscape: Landscape 
  file_characteristics: Maybe[SceneFileCharacteristics]
  characteristics: SceneCharacteristics

  # Note: The scene needs some way to specify how to T/S/R the landscape.
  # Note: The scene needs some way to specify the UOM of world coordinates.

from . import *