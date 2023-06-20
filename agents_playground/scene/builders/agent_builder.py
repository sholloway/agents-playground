from types import SimpleNamespace
from typing import Callable, Dict, List

from agents_playground.agents.default.default_agent_identity import DefaultAgentIdentity
from agents_playground.agents.default.default_agent_memory import DefaultAgentMemory
from agents_playground.agents.default.default_agent_movement_attributes import DefaultAgentMovementAttributes
from agents_playground.agents.default.default_agent_physicality import DefaultAgentPhysicality
from agents_playground.agents.default.default_agent_position import DefaultAgentPosition
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.default.default_agent_style import DefaultAgentStyle
from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_style_spec import AgentStyleLike
from agents_playground.agents.default.default_agent import DefaultAgent
from agents_playground.agents.systems.agent_nervous_system import AgentNervousSystem
from agents_playground.agents.systems.agent_perception_system import AgentPerceptionSystem
from agents_playground.core.types import Size
from agents_playground.renderers.color import Colors
from agents_playground.scene.id_map import IdMap
from agents_playground.scene.parsers.scene_parser_exception import SceneParserException
from agents_playground.scene.parsers.types import AgentStateName
from agents_playground.scene.scene_defaults import SceneDefaults
from agents_playground.spatial.aabbox import EmptyAABBox
from agents_playground.spatial.direction import Direction
from agents_playground.spatial.frustum import Frustum, Frustum2d
from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vector2d import Vector2d

class AgentBuilder:
  @staticmethod
  def build(
    id_generator: Callable, 
    id_map: IdMap, 
    agent_def: SimpleNamespace,
    cell_size: Size,
    agent_action_selector: AgentActionSelector,
    agent_state_definitions: Dict[AgentStateName, AgentActionStateLike],
    systems_map: Dict[str, Callable]
  ) -> AgentLike:
    """Create an agent instance from the TOML definition."""
    agent_identity = AgentBuilder.parse_identity(id_generator, agent_def)
    id_map.register_agent(agent_identity.id, agent_identity.toml_id)

    agent_size        = AgentBuilder.parse_agent_size()
    position          = AgentBuilder.parse_agent_position()
    agent_state       = AgentBuilder.parse_agent_state(agent_def, agent_action_selector, agent_state_definitions)
    frustum           = AgentBuilder.parse_view_frustum(agent_def)
    agent_physicality = AgentBuilder.parse_agent_physicality(agent_size, frustum)
    internal_systems  = AgentBuilder.parse_systems(agent_def, systems_map)

    agent = DefaultAgent(
      initial_state    = agent_state, 
      style            = AgentBuilder.parse_agent_style(),
      identity         = agent_identity,
      physicality      = agent_physicality,
      position         = position,
      movement         = DefaultAgentMovementAttributes(),
      agent_memory     = DefaultAgentMemory(),
      internal_systems = internal_systems
    )

    if hasattr(agent_def, 'crest'):
      agent.style.fill_color = Colors[agent_def.crest].value 

    if hasattr(agent_def, 'location'):
      agent.move_to(Coordinate(*agent_def.location), cell_size)

    if hasattr(agent_def, 'facing'):
      agent.face(Vector2d(*agent_def.facing), cell_size)
    
    return agent

  @staticmethod
  def parse_systems(agent_def: SimpleNamespace, systems_map: Dict[str, Callable]):
      internal_systems = DefaultAgentSystem('root-system')

      if not hasattr(agent_def, 'systems'):
        return internal_systems
      
      if not isinstance(agent_def.systems, List):
        err_msg = (
          f'Invalid scene.toml file.\n'
          f'An agent definition has a "systems field that is type {type(agent_def.systems)}.\n'
          f'agent.systems must be a list. Use the syntax: systems=["A","B", "C"].'
        )
        raise SceneParserException(err_msg)

      for sys_def in agent_def.systems:
        if not sys_def in systems_map:
          err_msg = (
            f'Invalid scene.toml file.\n'
            f'Agent {agent_def.id} declares systems=["{sys_def}"].\n'
            f'However, the system {sys_def} is not registered.\n'
            f'Use the agents_playground.project.extensions.register_system decorator to register an agent system function.'
          )
          raise SceneParserException(err_msg)
        internal_systems.register_system(systems_map[sys_def]())
      return internal_systems
      
  @staticmethod
  def parse_agent_physicality(agent_size, frustum):
      agent_physicality = DefaultAgentPhysicality(
      size = agent_size, 
      aabb = EmptyAABBox(),
      frustum = frustum
    )
      
      return agent_physicality

  @staticmethod
  def parse_view_frustum(agent_def):
      near_plane_depth: int = 10
      depth_of_field: int   = 100
      fov: int              = 120
      if hasattr(agent_def, 'near_plane_depth'):
        near_plane_depth = agent_def.near_plane_depth

      if hasattr(agent_def, 'depth_of_field'):
        depth_of_field = agent_def.depth_of_field
    
      if hasattr(agent_def, 'field_of_view'):
        fov = agent_def.field_of_view

      frustum: Frustum = Frustum2d(
      near_plane_depth = near_plane_depth, 
      depth_of_field = depth_of_field, 
      field_of_view = fov
    )
      
      return frustum

  @staticmethod
  def parse_agent_state(agent_def, agent_action_selector, agent_state_definitions):
    """
    Handle parsing the agent's state.
    """
    default_initial_state: AgentActionStateLike
    if len(agent_state_definitions) > 0:
      default_initial_state = list(agent_state_definitions.values())[0]
    else:
      default_initial_state = NamedAgentActionState('IDLE')

    initial_state: AgentActionStateLike 
    if hasattr(agent_def, 'state'):
      initial_state = agent_state_definitions.get(agent_def.state, default_initial_state)
    else: 
      initial_state = default_initial_state

    agent_state = DefaultAgentState(
      initial_state   = initial_state,
      action_selector = agent_action_selector
    )  
    return agent_state

  @staticmethod
  def parse_agent_position():
    """
    Handle getting the agent's position.
    """
    position = DefaultAgentPosition(
      facing            = Direction.EAST, 
      location          = Coordinate(0,0),
      last_location     = Coordinate(0,0),
      desired_location  = Coordinate(0,0) 
    )  
    return position

  @staticmethod
  def parse_agent_size():
    """
    Handle getting the agent's dimensions.
    """
    agent_size = Size(
      SceneDefaults.AGENT_STYLE_SIZE_WIDTH, 
      SceneDefaults.AGENT_STYLE_SIZE_HEIGHT
    ) 
    return agent_size

  @staticmethod
  def parse_identity(id_generator, agent_def):
    """
    Handle getting any IDs defined in the agent definition.
    """
    agent_identity = DefaultAgentIdentity(id_generator)
    agent_identity.toml_id = agent_def.id
    return agent_identity

  @staticmethod
  def parse_agent_style() -> AgentStyleLike:
    # Establish the agent style.
    # TODO: These should all be overridable in a scene file.
    return DefaultAgentStyle(
      stroke_thickness      = SceneDefaults.AGENT_STYLE_STROKE_THICKNESS,
      stroke_color          = SceneDefaults.AGENT_STYLE_STROKE_COLOR,
      fill_color            = SceneDefaults.AGENT_STYLE_FILL_COLOR,
      aabb_stroke_color     = SceneDefaults.AGENT_AABB_STROKE_COLOR,
      aabb_stroke_thickness = SceneDefaults.AGENT_AABB_STROKE_THICKNESS
    )