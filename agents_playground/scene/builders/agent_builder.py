from types import SimpleNamespace
from typing import Callable
from agents_playground.agents.default.default_agent_identity import DefaultAgentIdentity
from agents_playground.agents.default.default_agent_movement_attributes import DefaultAgentMovementAttributes
from agents_playground.agents.default.default_agent_physicality import DefaultAgentPhysicality
from agents_playground.agents.default.default_agent_position import DefaultAgentPosition
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.default.default_agent_style import DefaultAgentStyle
from agents_playground.agents.default.map_agent_action_selector import MapAgentActionSelector
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_style_spec import AgentStyleLike
from agents_playground.agents.default.default_agent import DefaultAgent

from agents_playground.agents.direction import Direction, Vector2d
from agents_playground.core.types import Coordinate, Size
from agents_playground.renderers.color import Colors

from agents_playground.scene.id_map import IdMap
from agents_playground.scene.scene_defaults import SceneDefaults

class AgentBuilder:
  @staticmethod
  def build(
    id_generator: Callable, 
    id_map: IdMap, 
    agent_def: SimpleNamespace,
    cell_size: Size
  ) -> AgentLike:
    """Create an agent instance from the TOML definition."""
    agent_identity = DefaultAgentIdentity(id_generator)
    agent_identity.toml_id = agent_def.id
    id_map.register_agent(agent_identity.id, agent_identity.toml_id)
    agent_size = Size(
      SceneDefaults.AGENT_STYLE_SIZE_WIDTH, 
      SceneDefaults.AGENT_STYLE_SIZE_HEIGHT
    )

    position = DefaultAgentPosition(
      facing            = Direction.EAST, 
      location          = Coordinate(0,0),
      last_location     = Coordinate(0,0),
      desired_location  = Coordinate(0,0) 
    )

    agent_state = DefaultAgentState(
      initial_state   = NamedAgentActionState('IDLE'),
      action_selector = MapAgentActionSelector(state_map = {}) # TODO: Make this driven by the TOML file.
    )

    agent = DefaultAgent(
      initial_state = agent_state, 
      style         = AgentBuilder.parse_agent_style(),
      identity      = agent_identity,
      physicality   = DefaultAgentPhysicality(size = agent_size),
      position      = position,
      movement      = DefaultAgentMovementAttributes()
    )

    if hasattr(agent_def, 'crest'):
      agent.style.fill_color = Colors[agent_def.crest].value 

    if hasattr(agent_def, 'location'):
      agent.move_to(Coordinate(*agent_def.location), cell_size)

    if hasattr(agent_def, 'facing'):
      agent.face(Vector2d(*agent_def.facing))
    
    if hasattr(agent_def, 'state'):
      agent.agent_state.assign_action_state(NamedAgentActionState(agent_def.state))

    return agent

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