from typing import Optional, Union

import dearpygui.dearpygui as dpg

from agents_playground.logger import log, setup_logging
from agents_playground.observe import Observable, Observer
from agents_playground.simulation import Simulation, SimulationEvents
from agents_playground.single_agent_simulation import SingleAgentSimulation


class PlaygroundApp(Observer):
  def __init__(self) -> None:
    dpg.create_context()
    self.primary_window_ref = dpg.generate_uuid()
    self.menu_items = {
      'sims': {
        'launch_single_agent_sim': dpg.generate_uuid()
      }
    }
    self._active_simulation: Union[Simulation, Observable, None] = None

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
    if msg == SimulationEvents.WINDOW_CLOSED.value and self._active_simulation is not None:
      self._active_simulation.detach(self)
      self._active_simulation = None