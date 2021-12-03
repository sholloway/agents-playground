from abc import ABC, abstractclassmethod, abstractmethod
from enum import Enum
from logging import Logger
import math
import threading
from time import sleep, perf_counter
from typing import Callable, List, Optional

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

class Observer(ABC):
  @abstractmethod
  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""    

    
class Observable:
  """
  A class that notifies subscribers of events.
  """
  def __init__(self) -> None:
    self._observers: List[Observer] = []

  def attach(self, observer: Observer) -> None:
    """
    Attach an observer to the subject.
    """
    self._observers.append(observer)

    
  def detach(self, observer: Observer) -> None:
    """
    Detach an observer from the subject.
    """
    if observer in self._observers:
      self._observers.remove(observer)

  
  def notify(self, msg: str) -> None:
    """
    Notify all observers about an event.
    """
    for observer in self._observers:
      observer.update(msg)

class SimulationEvents(Enum):
  WINDOW_CLOSED = 'WINDOW_CLOSED'

class PlaygroundApp(Observer):
  def __init__(self) -> None:
    dpg.create_context()
    self.primary_window_ref = dpg.generate_uuid()
    self.menu_items = {
      'sims': {
        'launch_single_agent_sim': dpg.generate_uuid()
      }
    }
    self._active_simulation: Optional[Simulation] = None

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
    if self._active_simulation is not None:
      """Only allow one active simulation at a time."""
      return

    if sender is self.menu_items['sims']['launch_single_agent_sim']:
      self._active_simulation = SingleAgentSimulation()
      self._active_simulation.attach(self)
      self._active_simulation.launch()

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""   
    if msg == SimulationEvents.WINDOW_CLOSED.value:
      self._active_simulation.detach(self)
      self._active_simulation = None
    
class Simulation(Observable):
  def __init__(self) -> None:
      super().__init__()
    
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

def parse_args() -> dict:
  import argparse
  parser = argparse.ArgumentParser(description='Intelligent Agents Playground')
  parser.add_argument('--log', type=str, dest='loglevel', default="INFO",help='The log level. DEBUG | INFO | WARNING | ERROR | CRITICAL')
  return vars(parser.parse_args())

def pulse(time:float):
  return 0.5*(1+math.sin(2 * math.pi * time))

def main():
  args: dict = parse_args()
  logger = setup_logging(args['loglevel'])
  logger.info("Starting Agent's Playground")
  app = PlaygroundApp()
  app.launch()

if __name__ == "__main__":
  main()