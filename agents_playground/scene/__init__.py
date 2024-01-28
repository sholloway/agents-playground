from dataclasses import dataclass

from agents_playground.cameras.camera import Camera
from agents_playground.fp import Maybe
from agents_playground.scene.scene_characteristics import SceneCharacteristics
from agents_playground.scene.scene_file_characteristics import SceneFileCharacteristics
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.vector.vector import Vector

@dataclass
class Scene:
  file_characteristics: Maybe[SceneFileCharacteristics]
  characteristics: SceneCharacteristics
  camera: Camera
  landscape: Landscape 
  # Vectors that define the translation, scale, and rotation of the landscape 
  # With relation to the scene's coordinate system.
  # Not part of the landscape since landscapes can be shared across scenes.
  landscape_location: Vector # Where the landscape's origin is in relation to the scene.
  landscape_scale: Vector    # How much to scale the landscape if any.
  landscape_rotation: Vector # How much to rotate the landscape around the scene's origin. 

from . import *