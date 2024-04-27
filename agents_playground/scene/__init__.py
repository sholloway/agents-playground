from dataclasses import dataclass
from math import radians
from typing import Any, cast

from agents_playground.agents.default.default_agent import DefaultAgent
from agents_playground.agents.default.default_agent_identity import DefaultAgentIdentity
from agents_playground.agents.default.default_agent_movement_attributes import DefaultAgentMovementAttributes
from agents_playground.agents.default.default_agent_physicality import DefaultAgentPhysicality
from agents_playground.agents.default.default_agent_position import DefaultAgentPosition
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.memory.agent_memory_model import AgentMemoryModel
from agents_playground.agents.no_agent import EmptyAgentState, EmptyAgentStyle, NoAgent
from agents_playground.agents.spec.agent_identity_spec import AgentIdentityLike
from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.agents.spec.agent_position_spec import AgentPositionLike
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_state_spec import AgentStateLike
from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.core.types import Size
from agents_playground.fp import Maybe, wrap_field_as_maybe
from agents_playground.id import next_id
from agents_playground.loaders.agent_definition_loader import AgentDefinition, AgentDefinitionLoader, FsmAgentStateModel
from agents_playground.loaders.landscape_loader import LandscapeLoader
from agents_playground.scene.scene_characteristics import SceneCharacteristics
from agents_playground.scene.scene_file_characteristics import SceneFileCharacteristics
from agents_playground.spatial.aabbox import EmptyAABBox
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.frustum import Frustum3d
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector import vector 
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

class SceneLoadingError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

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
    # agents: list[AgentLike]
    if not self.agents or len(self.agents) < 1 or not isinstance(self.agents[0], dict):
      return 
    
    agent_builder = SceneAgentBuilder(self.agent_definitions)
    self.agents = [ 
      agent_builder.build(agent_attributes) 
      for agent_attributes in self.agents 
      if isinstance(agent_attributes, dict)
    ]

class SceneAgentBuilder:
  def __init__(self, agent_definitions: dict[str, AgentDefinition]) -> None:
    self._agent_definitions = agent_definitions

  def build(self, agent_attributes: dict[str, Any]) -> AgentLike:
    try:
      agent_def: AgentDefinition        = self._agent_definition(agent_attributes)
      agent_position: AgentPositionLike = self._agent_position(agent_attributes)
      agent_identity: AgentIdentityLike = self._agent_identity(agent_attributes)   # TODO: Clean up DefaultAgentIdentity class after removing DearPyGUI.
      physicality                       = self._physicality(agent_def)
      memory                            = self._memory()
      agent_state: AgentStateLike       = self._agent_state(agent_def)

      agent = DefaultAgent(
        initial_state = agent_state,
        style         = EmptyAgentStyle(), # TODO: Get ride of AgentStyleLike.
        identity      = agent_identity,
        physicality   = physicality,
        position      = agent_position,
        movement      = DefaultAgentMovementAttributes(),
        agent_memory  = memory
      )
      return agent
    except KeyError as e:
      error_msg = 'Failed to load the scene.\nThere is an issue with loading one of the agents.'
      raise SceneLoadingError(error_msg) from e 
    
  def _agent_definition(self, agent_attributes: dict[str, Any]) -> AgentDefinition:
    agent_def_alias: str = agent_attributes['definition']
    return self._agent_definitions[agent_def_alias]
  
  def _agent_position(self, agent_attributes: dict[str, Any]) -> AgentPositionLike:
    agent_initial_location: list[float] = agent_attributes['location']
    agent_position = DefaultAgentPosition(
      facing           = vector(1, 0, 0), # For the moment make them all face parallel to the X-axis.
      location         = Coordinate(*agent_initial_location),
      last_location    = Coordinate(0,0,0),
      desired_location = Coordinate(0,0,0)
    )
    return agent_position
  
  def _agent_identity(self, agent_attributes: dict[str, Any]) -> AgentIdentityLike:
    agent_identity = DefaultAgentIdentity(id_generator=next_id)
    agent_identity.community_id = agent_attributes['id']
    return agent_identity
  
  def _physicality(self, agent_def: AgentDefinition) -> AgentPhysicalityLike:
    physicality = DefaultAgentPhysicality(
        size = Size(w=0, h=0), # TODO: Figure this out for 3D agents
        aabb = EmptyAABBox(),
        frustum = Frustum3d(
          near_plane_depth=agent_def.view_frustum.near_plane_depth, 
          depth_of_field=agent_def.view_frustum.depth_of_field, 
          field_of_view=agent_def.view_frustum.field_of_view
        )
      )
    return physicality
  
  def _memory(self) -> AgentMemoryModel:
    # TODO: Extend the Agent Definition contract to account for memory models.
    return AgentMemoryModel()
  
  def _agent_state(self, agent_def: AgentDefinition) -> AgentStateLike:
    agent_state: AgentStateLike
    if agent_def.agent_state_model.is_something():
      agent_state_model: FsmAgentStateModel = cast(
        FsmAgentStateModel, 
        agent_def.agent_state_model.unwrap()
      )

      agent_state = DefaultAgentState(
        initial_state = agent_state_model.initial_agent_state,
        action_selector = agent_state_model.state_transition_map,
        is_visible = True
      )
    else: 
      agent_state = EmptyAgentState()
    return agent_state

from . import *