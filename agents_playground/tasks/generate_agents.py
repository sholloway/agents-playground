"""
Module containing coroutines related to generating agents.
"""

from typing import cast
import dearpygui.dearpygui as dpg

from agents_playground.agents.agent import Agent, AgentActionState, AgentIdentity, AgentPhysicality, AgentState
from agents_playground.agents.direction import Direction
from agents_playground.core.types import Coordinate, Size
from agents_playground.navigation.navigation_mesh import Junction
from agents_playground.scene.scene import Scene
from agents_playground.scene.scene_defaults import SceneDefaults
from agents_playground.styles.agent_style import AgentStyle
from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

def generate_agents(*args, **kwargs):
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
    style = AgentStyle(
      stroke_thickness      = SceneDefaults.AGENT_STYLE_STROKE_THICKNESS,
      stroke_color          = SceneDefaults.AGENT_STYLE_STROKE_COLOR,
      fill_color            = (255, 255, 0),
      aabb_stroke_color     = SceneDefaults.AGENT_AABB_STROKE_COLOR,
      aabb_stroke_thickness = SceneDefaults.AGENT_AABB_STROKE_THICKNESS
    )

    initial_state = AgentState()
    agent_identity = AgentIdentity(dpg.generate_uuid)
    agent_size = Size( 
      SceneDefaults.AGENT_STYLE_SIZE_WIDTH, 
      SceneDefaults.AGENT_STYLE_SIZE_HEIGHT
    )

    new_agent = Agent(
      style         = style,
      initial_state = initial_state,
      identity      = agent_identity,
      physicality   = AgentPhysicality(size = agent_size),
      facing        = Direction.EAST
    )

    # 2. Assign an initial location.
    starting_location = select_starting_location(scene)
    new_agent.move_to(starting_location, scene.cell_size)

    # 3. Set the agent state to be in the planning state.
    # This will set the agent's in motion.
    new_agent.state.assign_action_state(AgentActionState.PLANNING)

    # 4. Add the agent to the scene.
    scene.add_agent(new_agent)
    
  logger.info('Task(generate_agents): Task Completed')

def select_starting_location(scene: Scene) -> Coordinate:
  # For now just put them all at Tower-1
  starting_junction: Junction = scene.nav_mesh.get_junction_by_toml_id('tower-1-apt-exit')
  return cast(Coordinate, starting_junction.location)

"""
Working through this current stupid bug...
- Things work ok for one agent but not >1. I'm wondering if this is a case of 
  shared memory (i.e. unintentional pointer) screwing things up.
- The desired_location isn't getting set. I think the 2nd agent isn't going through
  the planning state. Desired_location isn't being provisioned as class level field is it?

Thoughts
- The logic to jump to other states is leaky. Encapsulate that. 
  Have Agent.transition_state() be the only thing that can access AgentStateMap.
"""