"""
Module containing coroutines related to generating agents.
"""

from typing import cast
import dearpygui.dearpygui as dpg

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction
from agents_playground.core.types import Coordinate
from agents_playground.navigation.navigation_mesh import Junction
from agents_playground.scene.scene import Scene
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
    toml_id = dpg.generate_uuid()
    new_agent = Agent(
      crest = (255, 255, 0), 
      facing = Direction.EAST, 
      id = dpg.generate_uuid(), 
      render_id=toml_id, 
      toml_id=toml_id)

    # 2. Assign an initial location.
    starting_location = select_starting_location(scene)
    new_agent.move_to(starting_location, scene.agent_style.size, scene.cell_size)

    # 3. Add the agent to the scene.
    scene.add_agent(new_agent)
    
  logger.info('Task(generate_agents): Task Completed')

def select_starting_location(scene: Scene) -> Coordinate:
  # For now just put them all at Tower-1
  starting_junction: Junction = scene.nav_mesh.get_junction_by_toml_id('tower-1-apt-exit')
  return cast(Coordinate, starting_junction.location)