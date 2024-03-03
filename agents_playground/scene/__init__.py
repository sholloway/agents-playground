from dataclasses import dataclass

from agents_playground.cameras.camera import Camera
from agents_playground.fp import Maybe, wrap_field_as_maybe
from agents_playground.loaders.landscape_loader import LandscapeLoader
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
  # with relation to the scene's coordinate system.
  # They are not part of the landscape since landscapes can be shared across scenes.
  landscape_location: Vector # Where the landscape's origin is in relation to the scene.
  landscape_scale: Vector    # How much to scale the landscape if any.
  landscape_rotation: Vector # How much to rotate the landscape around the scene's origin. 

  def __post_init__(self) -> None:
    """Handle correctly initializing the Scene when loading from JSON."""
    wrap_field_as_maybe(self, 'file_characteristics', lambda f: SceneFileCharacteristics(**f))

    if isinstance(self.characteristics, dict):
      self.characteristics = SceneCharacteristics(**self.characteristics)
      
    # if isinstance(self.landscape, str):
    #   landscape_loader = LandscapeLoader()
    #   landscape_path: str = self.landscape
    #   self.landscape = landscape_loader.load(landscape_path)

from . import *