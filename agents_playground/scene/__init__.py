from dataclasses import dataclass
from math import radians

from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.fp import Maybe, wrap_field_as_maybe
from agents_playground.loaders.agent_definition_loader import AgentDefinition, AgentDefinitionLoader
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
  agent_definitions: dict[str, AgentDefinition]
  agents: list[AgentLike]


  def __post_init__(self) -> None:
    """Handle correctly initializing the Scene when loading from JSON."""
    wrap_field_as_maybe(self, 'file_characteristics', lambda f: SceneFileCharacteristics(**f))
    self._init_characteristics()
    self._init_camera()
    self._init_landscape()
    self._init_landscape_transformation()
    self._init_agent_definitions()
    self._init_agents()

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
    
    # 1. Grab the aspect ratio.
    aspect_ratio = self.camera['aspect_ratio']

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
      position     = position,
      target       = target,
      near_plane   = near_plane,
      far_plane    = far_plane,
      vertical_fov = v_fov_radians,
      aspect_ratio = aspect_ratio
    )

  def _init_landscape_transformation(self) -> None:
    if isinstance(self.landscape_transformation, dict):
      self.landscape_transformation = Transformation(**self.landscape_transformation)

  def _init_agent_definitions(self) -> None:
    """
    The Scene.json expects a list[dict[str, str]]. 
    This needs to be converted into a dict[alias, AgentDefinition].
    """
    if isinstance(self.agent_definitions, list):
      loader = AgentDefinitionLoader()
      loaded_agent_definitions: dict[str, AgentDefinition] = {}
      for agent_def in self.agent_definitions:
        alias = agent_def['alias'] # type: ignore
        definition_file = agent_def['definition'] # type: ignore
        loaded_agent_definitions[alias] = loader.load(definition_file)
      self.agent_definitions = loaded_agent_definitions

  def _init_agents(self) -> None:
    pass 

from . import *