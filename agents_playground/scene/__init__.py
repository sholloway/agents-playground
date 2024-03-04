from dataclasses import dataclass
from math import radians

from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.fp import Maybe, wrap_field_as_maybe
from agents_playground.loaders.landscape_loader import LandscapeLoader
from agents_playground.scene.scene_characteristics import SceneCharacteristics
from agents_playground.scene.scene_file_characteristics import SceneFileCharacteristics
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vector.vector3d import Vector3d

@dataclass
class Transformation:
  translation: Vector
  rotation: Vector
  scale: Vector 

  def __post_init__(self) -> None:
    if isinstance(self.translation, list):
      self.translation = Vector3d(*self.translation)

    if isinstance(self.rotation, list):
      self.rotation = Vector3d(*self.rotation)
  
    if isinstance(self.scale, list):
      self.scale = Vector3d(*self.scale)

@dataclass
class Scene:
  file_characteristics: Maybe[SceneFileCharacteristics]
  characteristics: SceneCharacteristics
  camera: Camera
  landscape: Landscape 
  landscape_transformation: Transformation

  def __post_init__(self) -> None:
    """Handle correctly initializing the Scene when loading from JSON."""
    wrap_field_as_maybe(self, 'file_characteristics', lambda f: SceneFileCharacteristics(**f))
    self._init_characteristics()
    self._init_camera()
    self._init_landscape()
    self._init_landscape_transformation()

  def _init_characteristics(self) -> None:
    if isinstance(self.characteristics, dict):
      self.characteristics = SceneCharacteristics(**self.characteristics)

  def _init_landscape(self) -> None:
    if isinstance(self.landscape, str):
      landscape_loader = LandscapeLoader()
      self.landscape = landscape_loader.load(self.landscape)

  def _init_camera(self) -> None:
    if not isinstance(self.camera, dict):
      # Only run this method if the camera is a dict.
      return
    
    # 1. Convert the AR from "Width:Height" to a float.
    width_str, height_str = self.camera['aspect_ratio'].split(':')
    aspect_ratio: float = float(width_str)/float(height_str)

    # 2. Convert the vertical field of view.
    v_fov_degrees = self.camera['vertical_field_of_view']
    v_fov_radians = radians(v_fov_degrees)

    # 3. Convert the arrays to vectors.
    position: Vector = Vector3d(*self.camera['position'])
    target: Vector = Vector3d(*self.camera['target'])

    # 4. Convert the boundary planes. 
    near_plane = self.camera['near_plane']
    far_plane = self.camera['far_plane']

    # 5. Build the camera.
    self.camera = Camera3d.look_at(
      position = position,
      target   = target,
      projection_matrix = Matrix4x4.perspective(
        aspect_ratio= aspect_ratio, 
        v_fov = v_fov_radians, 
        near = near_plane, 
        far = far_plane
      )
    )

  def _init_landscape_transformation(self) -> None:
    if isinstance(self.landscape_transformation, dict):
      self.landscape_transformation = Transformation(**self.landscape_transformation)

from . import *