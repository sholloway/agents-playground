
from agents_playground.agents.structures import Size
from agents_playground.core.event_based_simulation import EventBasedSimulation
from agents_playground.simulation.context import SimulationContext

class MultipleAgentsSim(EventBasedSimulation):
  def __init__(self) -> None:
    super().__init__()
    self._sim_description = 'Multiple agents all moving around.'
    self._sim_instructions = 'Click the start button to begin the simulation.'
    self._cell_size = Size(20, 20)
    self._cell_center_x_offset: float = self._cell_size.width/2
    self._cell_center_y_offset: float = self._cell_size.height/2
    
  # _bootstrap_simulation_render, _establish_context_ext, _sim_loop_tick
  def _establish_context_ext(self, context: SimulationContext) -> None:
    """Setup simulation specific context variables."""
    context.details['cell_size'] = self._cell_size
    context.details['cell_center_x_offset'] = self._cell_center_x_offset
    context.details['cell_center_y_offset'] = self._cell_center_y_offset

  def _bootstrap_simulation_render(self) -> None:
    pass

  def _sim_loop_tick(self, **args):
    """Handles one tick of the simulation."""
    pass