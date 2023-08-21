from types import SimpleNamespace
from typing import Callable, Dict, List

from agents_playground.agents.default.default_agent_identity import DefaultAgentIdentity
from agents_playground.agents.default.default_agent_movement_attributes import DefaultAgentMovementAttributes
from agents_playground.agents.default.default_agent_physicality import DefaultAgentPhysicality
from agents_playground.agents.default.default_agent_position import DefaultAgentPosition
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.default.default_agent_style import DefaultAgentStyle
from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.memory.agent_memory_model import AgentMemoryModel
from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_identity_spec import AgentIdentityLike
from agents_playground.agents.spec.agent_memory_spec import AgentMemoryLike
from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.agents.spec.agent_position_spec import AgentPositionLike
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_state_spec import AgentStateLike
from agents_playground.agents.spec.agent_style_spec import AgentStyleLike
from agents_playground.agents.default.default_agent import DefaultAgent
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

DEFAULT_NEAR_PLANE_DEPTH: int = 10
DEFAULT_DEPTH_OF_FIELD: int   = 100
DEFAULT_FOV: int              = 120

def _parse_agent_memory() -> AgentMemoryLike:
  """
  Handle building the agent's memory store.
  """
  agent_memory = AgentMemoryModel()
  return agent_memory
  
def _parse_systems(agent_def: SimpleNamespace, systems_map: Dict[str, Callable]):
  """
  Handle building the agent's internal systems.
  """
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
      
def _parse_agent_physicality(agent_size: Size, frustum: Frustum) -> AgentPhysicalityLike:
  """
  Handle building the agent's physicality.
  """
  agent_physicality = DefaultAgentPhysicality(
    size = agent_size, 
    aabb = EmptyAABBox(),
    frustum = frustum
  )  
  return agent_physicality

def _parse_view_frustum(agent_def: SimpleNamespace) -> Frustum:
  """
  Handle building the agent's view frustum.
  """
  near_plane_depth: int = agent_def.near_plane_depth if hasattr(agent_def, 'near_plane_depth') else DEFAULT_NEAR_PLANE_DEPTH
  depth_of_field: int   = agent_def.depth_of_field if hasattr(agent_def, 'depth_of_field') else DEFAULT_DEPTH_OF_FIELD
  fov: int              = agent_def.field_of_view if hasattr(agent_def, 'field_of_view') else DEFAULT_FOV

  frustum: Frustum = Frustum2d(
    near_plane_depth = near_plane_depth, 
    depth_of_field = depth_of_field, 
    field_of_view = fov
  )  
  return frustum

def _parse_agent_state(
  agent_def: SimpleNamespace, 
  agent_action_selector: AgentActionSelector, 
  agent_state_definitions: Dict[AgentStateName, AgentActionStateLike]
) -> AgentStateLike:
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

def _parse_agent_position() -> AgentPositionLike:
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

def _parse_agent_size() -> Size:
  """
  Handle getting the agent's dimensions.
  """
  agent_size = Size(
    SceneDefaults.AGENT_STYLE_SIZE_WIDTH, 
    SceneDefaults.AGENT_STYLE_SIZE_HEIGHT
  ) 
  return agent_size

def _parse_identity(
  id_generator: Callable, 
  agent_def: SimpleNamespace
) -> AgentIdentityLike:
  """
  Handle getting any IDs defined in the agent definition.
  """
  agent_identity = DefaultAgentIdentity(id_generator)
  agent_identity.toml_id = agent_def.id
  return agent_identity

def _parse_agent_style(agent_def: SimpleNamespace) -> AgentStyleLike:
  """
  Handle building the agent's style.
  """
  # Establish the agent style.
  fill_color = Colors[agent_def.crest].value if hasattr(agent_def, 'crest') else SceneDefaults.AGENT_STYLE_FILL_COLOR

  # TODO: These should all be overridable in a scene file.
  return DefaultAgentStyle(
    stroke_thickness      = SceneDefaults.AGENT_STYLE_STROKE_THICKNESS,
    stroke_color          = SceneDefaults.AGENT_STYLE_STROKE_COLOR,
    fill_color            = fill_color,
    aabb_stroke_color     = SceneDefaults.AGENT_AABB_STROKE_COLOR,
    aabb_stroke_thickness = SceneDefaults.AGENT_AABB_STROKE_THICKNESS
  )

class AgentBuilder:
  """
  Build an agent based on its definition in a scene.toml file.
  """
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
    agent_identity = _parse_identity(id_generator, agent_def)
    id_map.register_agent(agent_identity.id, agent_identity.toml_id)

    agent = DefaultAgent(
      initial_state = _parse_agent_state(
        agent_def, 
        agent_action_selector, 
        agent_state_definitions
      ), 
      style       = _parse_agent_style(agent_def),
      identity    = agent_identity,
      physicality = _parse_agent_physicality(
        _parse_agent_size(), 
        _parse_view_frustum(agent_def)
        ),
      position         = _parse_agent_position(),
      movement         = DefaultAgentMovementAttributes(),
      agent_memory     = _parse_agent_memory(),
      internal_systems = _parse_systems(agent_def, systems_map)
    )

    if hasattr(agent_def, 'location'):
      agent.move_to(Coordinate(*agent_def.location), cell_size)

    if hasattr(agent_def, 'facing'):
      agent.face(Vector2d(*agent_def.facing), cell_size)
    
    return agent