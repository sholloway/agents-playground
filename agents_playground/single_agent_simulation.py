import math
import threading
from time import sleep, perf_counter

import dearpygui.dearpygui as dpg

from simulation import Simulation, SimulationEvents

class SingleAgentSimulation(Simulation):
  def __init__(self) -> None:
    super().__init__()
    self.circle_node_ref = dpg.generate_uuid()
    self.circle_ref = dpg.generate_uuid()

  def launch(self):
    with dpg.window(label="Single Agent Simulation", width=400, height=400, on_close=self._handle_sim_closed):
      dpg.add_text("Baby steps...")
    
      # Create a drawing canvas
      with dpg.drawlist(width=400, height=400): 
        with dpg.draw_node(tag=self.circle_node_ref):
          dpg.draw_circle(tag=self.circle_ref, center = [0,0], radius=20, color=[0, 0, 0], fill=[0, 0, 255])
  
    dpg.apply_transform(self.circle_node_ref, dpg.create_translation_matrix([250, 250]))  

    # Create a thread for updating the simulation.
    sim_thread = threading.Thread(name="single-agent-thread", target=self._sim_loop, args=(), daemon=True)
    sim_thread.start()

  def _handle_sim_closed(self, sender, app_data, user_data):
    super().notify(SimulationEvents.WINDOW_CLOSED.value)

  def _sim_loop(self, **args):
    # for now just have the radius pulsate.
    default_radius: float = 20
    scale:float = 10

    while True:
      sleep(0.100) 
      inflat:float = pulse(perf_counter())
      new_radius = default_radius + scale * inflat
      dpg.configure_item(self.circle_ref, radius = new_radius)

def pulse(time:float):
  return 0.5*(1+math.sin(2 * math.pi * time))