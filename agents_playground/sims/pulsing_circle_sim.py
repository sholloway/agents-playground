import math
from time import  perf_counter

import dearpygui.dearpygui as dpg
from agents_playground.core.simulation import Simulation
from agents_playground.simulation.context import SimulationContext

class PulsingCircleSim(Simulation):
  def __init__(self) -> None:
    super().__init__()
    self.circle_node_ref = dpg.generate_uuid()
    self.circle_ref = dpg.generate_uuid()
    self.simulation_title = "Pulsing Circle Simulation"
    self._default_radius: float = 20
    self._scale: float = 10
    self._sim_run_rate = 0.100 # Override the default rate.
    self.add_layer(render_circles, 'Circles')

  def _initial_render(self) -> None:
    """Define the render setup for when the simulation has been launched but not started."""
    pass

  def _bootstrap_simulation_render(self) -> None:
    """Define the render setup for when the render is started."""    
    dpg.apply_transform(self.circle_node_ref, dpg.create_translation_matrix([250, 250]))  

  def _sim_loop_tick(self, **args):
    """Handles one tick of the simulation."""
    inflat: float = pulse(perf_counter())
    new_radius = self._default_radius + self._scale * inflat
    dpg.configure_item(self.circle_ref, radius = new_radius)

  def _setup_menu_bar_ext(self) -> None:
    """Setup simulation specific menu items."""
    pass

  def _establish_context_ext(self, context: SimulationContext) -> None:
    """Setup simulation specific context variables."""
    context.details['circle_node_ref'] = self.circle_node_ref
    context.details['circle_ref'] = self.circle_ref

def pulse(time:float):
  return 0.5*(1+math.sin(2 * math.pi * time))

def render_circles(**data) -> None:
  context = data['context']
  with dpg.draw_node(tag=context.details['circle_node_ref']):
    dpg.draw_circle(
      tag=context.details['circle_ref'], 
      center = [0,0], 
      radius=20, 
      color=[0, 0, 0], 
      fill=[0, 0, 255])
