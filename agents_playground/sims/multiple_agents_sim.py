
from typing import List

from agents_playground.agents.agent import Agent
from agents_playground.agents.structures import Size
from agents_playground.core.event_based_simulation import EventBasedSimulation
from agents_playground.renderers.agent import render_agents
from agents_playground.renderers.grid import render_grid
from agents_playground.renderers.path import render_path
from agents_playground.simulation.context import SimulationContext
from agents_playground.renderers.color import BasicColors

class MultipleAgentsSim(EventBasedSimulation):
  def __init__(self) -> None:
    super().__init__()
    self._sim_description = 'Multiple agents all moving around.'
    self._sim_instructions = 'Click the start button to begin the simulation.'
    self._cell_size = Size(20, 20)
    self._cell_center_x_offset: float = self._cell_size.width/2
    self._cell_center_y_offset: float = self._cell_size.height/2
    self._agents: List[Agent] = []
    self.add_layer(render_grid, 'Terrain')
    self.add_layer(render_path, 'Path')
    self.add_layer(render_agents, 'Agents')
    self._setup_agents(self._agents)
    
  # _bootstrap_simulation_render, _establish_context_ext, _sim_loop_tick
  def _establish_context_ext(self, context: SimulationContext) -> None:
    """Setup simulation specific context variables."""
    context.details['cell_size'] = self._cell_size
    context.details['cell_center_x_offset'] = self._cell_center_x_offset
    context.details['cell_center_y_offset'] = self._cell_center_y_offset

  def _bootstrap_simulation_render(self) -> None:
    pass

  def _sim_loop_tick(self, **args) -> None:
    """Handles one tick of the simulation."""
    pass

  def _setup_agents(self, agents) -> None:
    agents: List[Agent] = []

    # Have 4 agents on the same path, going the same direction.
    agent1 = Agent(crest=BasicColors.aqua)
    agent2 = Agent(crest=BasicColors.aqua)
    agent3 = Agent(crest=BasicColors.aqua)
    agent4 = Agent(crest=BasicColors.aqua)