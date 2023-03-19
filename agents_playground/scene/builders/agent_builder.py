from types import SimpleNamespace
from typing import Callable
from agents_playground.agents.agent import Agent, AgentActionState, AgentIdentity, AgentMovement, AgentPhysicality, AgentPosition, AgentState
from agents_playground.agents.direction import Direction, Vector2d
from agents_playground.core.types import Coordinate, Size
from agents_playground.renderers.color import Colors

from agents_playground.scene.id_map import IdMap
from agents_playground.scene.scene_defaults import SceneDefaults
from agents_playground.styles.agent_style import AgentStyle


class AgentBuilder:
  @staticmethod
  def build(
    id_generator: Callable, 
    id_map: IdMap, 
    agent_def: SimpleNamespace,
    cell_size: Size
  ) -> Agent:
    """Create an agent instance from the TOML definition."""
    agent_identity = AgentIdentity(id_generator)
    agent_identity.toml_id = agent_def.id
    id_map.register_agent(agent_identity.id, agent_identity.toml_id)
    agent_size = Size(
      SceneDefaults.AGENT_STYLE_SIZE_WIDTH, 
      SceneDefaults.AGENT_STYLE_SIZE_HEIGHT
    )

    position = AgentPosition(
      facing            = Direction.EAST, 
      location          = Coordinate(0,0),
      last_location     = Coordinate(0,0),
      desired_location  = Coordinate(0,0) 
    )

    agent = Agent(
      initial_state = AgentState(), 
      style         = AgentBuilder.parse_agent_style(),
      identity      = agent_identity,
      physicality   = AgentPhysicality(size = agent_size),
      position      = position,
      movement      = AgentMovement()
    )

    if hasattr(agent_def, 'crest'):
      agent.style.fill_color = Colors[agent_def.crest].value 

    if hasattr(agent_def, 'location'):
      agent.move_to(Coordinate(*agent_def.location), cell_size)

    if hasattr(agent_def, 'facing'):
      agent.face(Vector2d(*agent_def.facing))
    
    if hasattr(agent_def, 'state'):
      agent.state.assign_action_state(AgentActionState[agent_def.state])

    return agent

  @staticmethod
  def parse_agent_style() -> AgentStyle:
    # Establish the agent style.
    # TODO: These should all be overridable in a scene file.
    return AgentStyle(
      stroke_thickness      = SceneDefaults.AGENT_STYLE_STROKE_THICKNESS,
      stroke_color          = SceneDefaults.AGENT_STYLE_STROKE_COLOR,
      fill_color            = SceneDefaults.AGENT_STYLE_FILL_COLOR,
      aabb_stroke_color     = SceneDefaults.AGENT_AABB_STROKE_COLOR,
      aabb_stroke_thickness = SceneDefaults.AGENT_AABB_STROKE_THICKNESS
    )