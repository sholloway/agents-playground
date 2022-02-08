
import itertools
from typing import List, Optional

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction
from agents_playground.agents.path import AgentAction, AgentPath, AgentStep, IdleStep
from agents_playground.agents.structures import Point, Size
from agents_playground.core.event_based_simulation import EventBasedSimulation
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
  
class MultipleAgentsSim(EventBasedSimulation):
  def __init__(self) -> None:
    super().__init__()
    logger.info('MultipleAgentsSim: Initializing')
    self._sim_description = 'Multiple agents all moving around.'
    self._sim_instructions = 'Click the start button to begin the simulation.'
    self._cell_size = Size(20, 20)
    self._cell_center_x_offset: float = self._cell_size.width/2
    self._cell_center_y_offset: float = self._cell_size.height/2
    self._agent_node_refs: List[Tag] = []
    self._agents: List[Agent] = []
    self._paths: List[AgentPath] = self._build_paths()
    self.add_layer(render_grid, 'Terrain')
    self.add_layer(render_paths, 'Path')
    self.add_layer(render_agents, 'Agents')
    self._setup_agents(self._agents)
    
  def _build_paths(self) -> List[AgentPath]:
    logger.info('MultipleAgentsSim: Building agent paths')
    path_a = [
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
    return [path_a]
  
  # _bootstrap_simulation_render, _establish_context_ext, _sim_loop_tick
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
    pass

  def _sim_loop_tick(self, **args) -> None:
    """Handles one tick of the simulation."""
    pass

  def _setup_agents(self, agents) -> None:
    logger.info('MultipleAgentsSim: Setting up agents')
    agents: List[Agent] = []

    # Have 4 agents on the same path (path_a), going the same direction.
    agent1 = Agent(crest=BasicColors.aqua)
    agent2 = Agent(crest=BasicColors.aqua)
    agent3 = Agent(crest=BasicColors.aqua)
    agent4 = Agent(crest=BasicColors.aqua)