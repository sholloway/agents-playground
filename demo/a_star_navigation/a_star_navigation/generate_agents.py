"""
Module containing coroutines related to generating agents.
"""

from typing import cast
import dearpygui.dearpygui as dpg

from agents_playground.agents.default.default_agent import DefaultAgent
from agents_playground.agents.default.default_agent_identity import DefaultAgentIdentity
from agents_playground.agents.default.default_agent_memory import DefaultAgentMemory
from agents_playground.agents.default.default_agent_physicality import DefaultAgentPhysicality
from agents_playground.agents.default.default_agent_position import DefaultAgentPosition
from agents_playground.agents.default.default_agent_state import DefaultAgentState
from agents_playground.agents.default.default_agent_style import DefaultAgentStyle

from agents_playground.project.extensions import register_task
from agents_playground.agents.direction import Direction
from agents_playground.core.types import Coordinate, Size
from agents_playground.navigation.navigation_mesh import Junction
from agents_playground.renderers.color import Color
from agents_playground.scene.scene import Scene
from agents_playground.scene.scene_defaults import SceneDefaults
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()

from a_star_navigation.agent_states import AgentStateNames
from a_star_navigation.agent_states import PathConstrainedAgentMovement


@register_task(label='generate_agents')
def generate_agents(*args, **kwargs) -> None:
  """A one time task that generates a batch of agents.

  Args:
    - scene: The scene to take action on.
    - initial_agent_count: The amount of agents to create.
  """
  logger.info('Task(generate_agents): Starting task.')
  scene: Scene = kwargs['scene']
  initial_agent_count: int = kwargs['initial_agent_count']
  
  for _ in range(initial_agent_count):
    # 1. Create an agent.
    style = DefaultAgentStyle(
      stroke_thickness      = SceneDefaults.AGENT_STYLE_STROKE_THICKNESS,
      stroke_color          = SceneDefaults.AGENT_STYLE_STROKE_COLOR,
      fill_color            = Color(255, 255, 0),
      aabb_stroke_color     = SceneDefaults.AGENT_AABB_STROKE_COLOR,
      aabb_stroke_thickness = SceneDefaults.AGENT_AABB_STROKE_THICKNESS
    )


    initial_state = DefaultAgentState(
      initial_state = scene.agent_state_definitions[AgentStateNames.IDLE_STATE.name], 
      action_selector = scene.agent_transition_maps['default_agent_state_map'] 
    )

    agent_identity = DefaultAgentIdentity(dpg.generate_uuid)
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
    
    new_agent = DefaultAgent(
      style         = style,
      initial_state = initial_state,
      identity      = agent_identity,
      physicality   = DefaultAgentPhysicality(size = agent_size),
      position      = position,
      agent_memory  = DefaultAgentMemory(),
      movement      = PathConstrainedAgentMovement()
    )

    # 2. Assign an initial location.
    starting_location = select_starting_location(scene)
    new_agent.move_to(starting_location, scene.cell_size)

    # 3. Set the agent state to be in the planning state.
    # This will set the agent's in motion.
    new_agent.agent_state.assign_action_state(scene.agent_state_definitions[AgentStateNames.PLANNING_STATE.name])

    # 4. Add the agent to the scene.
    scene.add_agent(new_agent)
    
  logger.info('Task(generate_agents): Task Completed')

def select_starting_location(scene: Scene) -> Coordinate:
  # For now just put them all at Tower-1
  starting_junction: Junction = scene.nav_mesh.get_junction_by_toml_id('tower-1-apt-exit')
  return cast(Coordinate, starting_junction.location)