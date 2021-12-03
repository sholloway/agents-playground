from logging import Logger
import math
import threading
from time import sleep, perf_counter
from typing import Optional

import dearpygui.dearpygui as dpg

from logger import log, setup_logging
from profile_tools import timer, size

"""
What is the abstraction here?
App
  Simulation
    Renderer
    Agent(s)
    Terrain
    Path
"""

class PlaygroundApp:
  def __init__(self) -> None:
    dpg.create_context()
    self.primary_window_ref = dpg.generate_uuid()
    self.menu_items = {
      'sims': {
        'launch_single_agent_sim': dpg.generate_uuid()
      }
    }
    self.active_simulation: Optional[Simulation] = None

  @log
  def launch(self) -> None:
    """Run the application"""
    self._configure_primary_window()
    self._setup_menu_bar()
    dpg.setup_dearpygui() # Assign the viewport
    dpg.show_viewport()
    dpg.set_primary_window(self.primary_window_ref, True)
    dpg.start_dearpygui()
    dpg.destroy_context()

  def _configure_primary_window(self):
    """Configure the Primary Window (the hosting window)."""
    with dpg.window(tag=self.primary_window_ref):
      pass
    dpg.create_viewport(title="Intelligent Agent Playground")

  def _setup_menu_bar(self):
    """Configure the primary window's menu bar."""
    with dpg.viewport_menu_bar():
      with dpg.menu(label="Simulations"):
        # dpg.add_menu_item(label="Single Agent", callback=launch_single_agent_sim, tag=self.menu_items['sims']['launch_single_agent_sim'])
        dpg.add_menu_item(label="Single Agent", callback=self._launch_simulation, tag=self.menu_items['sims']['launch_single_agent_sim'])

  def _launch_simulation(self, sender, item_data, user_data):
    if self.active_simulation is not None:
      """Only allow one active simulation at a time."""
      return

    if sender is self.menu_items['sims']['launch_single_agent_sim']:
      self.active_simulation = SingleAgentSimulation()
      self.active_simulation.launch()
    
    
class Simulation:
  pass
    
class SingleAgentSimulation(Simulation):
  def __init__(self) -> None:
    pass

  def launch(self):
    with dpg.window(label="Single Agent Simulation", width=400, height=400):
      dpg.add_text("Baby steps...")
    
      # Create a drawing canvas
      with dpg.drawlist(label="My Drawlist", width=400, height=400): 
        with dpg.draw_node(label="My Node", tag="circle-node"):
          dpg.draw_circle(tag="my-circle", center = [0,0], radius=20, color=[0, 0, 0], fill=[0, 0, 255])
  
    dpg.apply_transform("circle-node", dpg.create_translation_matrix([250, 250]))  

    # Create a thread for updating the simulation.
    sim_thread = threading.Thread(name="single-agent-thread", target=self._sim_loop, args=(), daemon=True)
    sim_thread.start()

  def _sim_loop(self, **args):
    # for now just have the radius pulsate.
    default_radius: float = 20
    scale:float = 10

    while True:
      sleep(0.100) 
      inflat:float = pulse(perf_counter())
      new_radius = default_radius + scale * inflat
      dpg.configure_item('my-circle',radius = new_radius)

def parse_args() -> dict:
  import argparse
  parser = argparse.ArgumentParser(description='Intelligent Agents Playground')
  parser.add_argument('--log', type=str, dest='loglevel', default="INFO",help='The log level. DEBUG | INFO | WARNING | ERROR | CRITICAL')
  return vars(parser.parse_args())

def pulse(time:float):
  # frequency: float = 10; # Frequency in Hz
  return 0.5*(1+math.sin(2 * math.pi * time))

def main():
  args: dict = parse_args()
  logger = setup_logging(args['loglevel'])
  logger.info("Starting Agent's Playground")
  app = PlaygroundApp()
  app.launch()

if __name__ == "__main__":
  main()