import math
import threading
from time import sleep, perf_counter

import dearpygui.dearpygui as dpg
from agents_playground.core.simulation import Simulation, SimulationState

class PulsingCircleSim(Simulation):
  def __init__(self) -> None:
    super().__init__()
    self.circle_node_ref = dpg.generate_uuid()
    self.circle_ref = dpg.generate_uuid()
    self.simulation_title = "Pulsing Circle Simulation"
    self._default_radius: float = 20
    self._scale: float = 10
    self._sim_run_rate = 0.100 # Override the default rate.
    

  def _initial_render(self) -> None:
    """Define the render setup for when the simulation has been launched but not started."""
    pass

  def _bootstrap_simulation_render(self) -> None:
    """Define the render setup for when the render is started."""
    # Create a drawing canvas
    with dpg.drawlist(parent=self._sim_window_ref, width=400, height=400): 
      with dpg.draw_node(tag=self.circle_node_ref):
        dpg.draw_circle(tag=self.circle_ref, center = [0,0], radius=20, color=[0, 0, 0], fill=[0, 0, 255])
  
    dpg.apply_transform(self.circle_node_ref, dpg.create_translation_matrix([250, 250]))  

  def _sim_loop_tick(self, **args):
    """Handles one tick of the simulation."""
    inflat: float = pulse(perf_counter())
    new_radius = self._default_radius + self._scale * inflat
    dpg.configure_item(self.circle_ref, radius = new_radius)

  def _setup_menu_bar_ext(self) -> None:
    """Setup simulation specific menu items."""
    pass

def pulse(time:float):
  return 0.5*(1+math.sin(2 * math.pi * time))