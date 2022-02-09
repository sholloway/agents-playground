
from dataclasses import dataclass
import itertools
from typing import Dict, List, Optional

import dearpygui.dearpygui as dpg

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction
from agents_playground.agents.path import AgentAction, AgentPath, AgentStep, IdleStep
from agents_playground.agents.structures import Point, Size
from agents_playground.core.event_based_simulation import EventBasedSimulation
from agents_playground.core.task_based_simulation import TaskBasedSimulation
from agents_playground.core.time_utilities import TIME_PER_FRAME, TimeInMS
from agents_playground.renderers.agent import render_agents
from agents_playground.renderers.grid import render_grid
from agents_playground.renderers.path import render_paths
from agents_playground.sims.event_based_agents import FutureAction
from agents_playground.simulation.context import SimulationContext
from agents_playground.renderers.color import BasicColors
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()

TIME_PER_STEP = TIME_PER_FRAME * 6
def sh(x: int, y: int, dir: Optional[Direction] = None, cost: TimeInMS=TIME_PER_STEP) -> FutureAction:
  """Convenance function for building a scheduled path step.
  
  Args:
    x: The tile/cell horizontal location to move to in the step.
    y: The tile/cell vertical location to move to in the step.
    dir: The direction the agent should face. 
    when: The number of milliseconds to when the action should be invoked.

  Returns:
    An action for an agent to take in the future.
  """
  action = AgentStep(Point(x,y), dir)
  return FutureAction(cost, action)

@dataclass
class Scene:
  agents: Dict[Tag, Agent]
  paths: Dict[Tag, AgentPath]

  def __init__(self) -> None:
    pass

  def add_agent(self, agent: Agent) -> None:
    self._agents[agent.id] = agent

  def add_path(self, path: AgentPath) -> None:
    self._paths[path.id] = path

  def path(self, path_id: Tag) -> Optional[AgentPath]:
    return self._paths[path_id] if path_id in self._paths else None
  
class MultipleAgentsSim(TaskBasedSimulation):
  def __init__(self) -> None:
    super().__init__()
    logger.info('MultipleAgentsSim: Initializing')
    self._sim_description = 'Multiple agents all moving around.'
    self._sim_instructions = 'Click the start button to begin the simulation.'
    self._cell_size = Size(20, 20)
    self._cell_center_x_offset: float = self._cell_size.width/2
    self._cell_center_y_offset: float = self._cell_size.height/2
    self._scene = Scene()
    self._setup_scene(self._scene)
    self.add_layer(render_grid, 'Terrain')
    self.add_layer(render_paths, 'Path')
    self.add_layer(render_agents, 'Agents')
    
  def _setup_scene(self, scene: Scene) -> None:
    logger.info('MultipleAgentsSim: Setting up the scene')

    path_a = self._create_path_a()
    scene.add_path(path_a)

    # Have 4 agents on the same path (path_a), going the same direction.
    a1 = Agent(crest=BasicColors.aqua, id=dpg.generate_uuid())
    a2 = Agent(crest=BasicColors.aqua, id=dpg.generate_uuid())
    a3 = Agent(crest=BasicColors.aqua, id=dpg.generate_uuid())
    a4 = Agent(crest=BasicColors.aqua, id=dpg.generate_uuid())

    # TODO Can the scene act as more of a DSL for building this stuff up?
    # This type of code shouldn't be in the MultipleAgentsSim class.
    scene.add_agent(a1)
    scene.add_agent(a2)
    scene.add_agent(a3)
    scene.add_agent(a4)

    # Just make this work for one agent at the moment.
    self._task_scheduler.add_task(
      agent_traverse_path, 
      [], 
      {
        'path_id': path_a.id,
        'agent_id': a1.id,
        'step_index': 0,
        'scene': scene
      }
    )

  def _create_path_a(self) -> AgentPath:
    logger.info('MultipleAgentsSim: Building agent paths')
    path = [
      # Walk 5 steps East.
      sh(9,4, Direction.EAST), sh(10,4), sh(11,4), sh(12,4), sh(13,4), sh(14,4),
      # Walk 3 steps south
      sh(14, 5, Direction.SOUTH), sh(14, 6), sh(14, 7),
      # Walk 6 steps to the East
      sh(15, 7, Direction.EAST), sh(16, 7), sh(17, 7), sh(18, 7), sh(19, 7), sh(20, 7),
      # Walk 2 steps south
      sh(20, 8, Direction.SOUTH), sh(20, 9),
      # Walk 8 steps to the West
      sh(19, 9, Direction.WEST), sh(18, 9, Direction.WEST), sh(17, 9, Direction.WEST), sh(16, 9, Direction.WEST), sh(15, 9, Direction.WEST), sh(14, 9, Direction.WEST), sh(13, 9, Direction.WEST), sh(12, 9, Direction.WEST),
      ## Walk North 3 steps
      sh(12, 8, Direction.NORTH), sh(12, 7), sh(12, 6), 
      # Walk West 3 steps
      sh(11, 6, Direction.WEST), sh(10, 6), sh(9, 6),
      # Walk North
      sh(9, 5, Direction.NORTH)
    ]
    return AgentPath(dpg.generate_uuid(), path)
  
  def _establish_context_ext(self, context: SimulationContext) -> None:
    """Setup simulation specific context variables."""
    logger.info('MultipleAgentsSim: Establishing simulation context.')
    context.details['cell_size'] = self._cell_size
    context.details['cell_center_x_offset'] = self._cell_center_x_offset
    context.details['cell_center_y_offset'] = self._cell_center_y_offset
    context.details['paths'] = self._paths
    context.details['agent_node_refs'] = self._agent_node_refs

  def _bootstrap_simulation_render(self) -> None:
    logger.info('MultipleAgentsSim: Bootstrapping simulation renderer')
    # I think this is where everything needs to get wired together.
    

  def _sim_loop_tick(self, **args) -> None:
    """Handles one tick of the simulation."""
    pass
    
"""
Design Questions/Thoughts
- The life cycle methods of a simulation is convoluted. This isn't saving any time.
- Better to have a task per agent or a task to update all tasks?
- How to deal with timing? 

Create a task that moves an agent one step on a path.
"""
def agent_traverse_path(*args, **kwargs):
  """A task that moves an agent along a path.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - step_index: The starting point on the path.
  """
  logger.info('agent_traverse_path: Starting task.')
  scene = kwargs['scene']
  agent_id = kwargs['agent_id']
  path_id = kwargs['path_id']
  step_index = kwargs['step_index']
  scene = kwargs['scene']
  ts = kwargs['ts']
  path = scene.path(path_id)
  try:
    while True:
      step_index = step_index + 1 if step_index < len(path) - 1 else 0
      step = path.step(step_index)

      # How to handle this?
      yield
  except GeneratorExit:
    logger.info('Task: agent_update - GeneratorExit')
  finally:
    print('Task: agent_update - task completed')