from typing import Optional, Union

import dearpygui.dearpygui as dpg

from agents_playground.core.logger import log, setup_logging
from agents_playground.core.observe import Observable, Observer
from agents_playground.sims.pulsing_circle_sim import PulsingCircleSim
from agents_playground.core.simulation import Simulation, SimulationEvents
from agents_playground.sims.single_agent_simulation import SingleAgentSimulation


class PlaygroundApp(Observer):
  def __init__(self) -> None:
    self._enable_windows_context()
    self._primary_window_ref = dpg.generate_uuid()
    self._menu_items = {
      'sims': {
        'launch_single_agent_sim': dpg.generate_uuid(),
        'pulsing_circle_sim': dpg.generate_uuid()
      }
    }
    self._active_simulation: Union[Simulation, Observable, None] = None

  @log
  def launch(self) -> None:
    """Run the application"""
    self._configure_primary_window()
    self._setup_menu_bar()
    dpg.setup_dearpygui() # Assign the viewport
    dpg.show_viewport(maximized=True)
    dpg.set_primary_window(self._primary_window_ref, True)
    dpg.maximize_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""   
    if msg == SimulationEvents.WINDOW_CLOSED.value and self._active_simulation is not None:
      self._active_simulation.detach(self)
      self._active_simulation = None

  @property
  def active_simulation(self) -> Union[Simulation, Observable, None]:
    return self._active_simulation

  def _enable_windows_context(self) -> None:
    dpg.create_context()

  def _configure_primary_window(self):
    """Configure the Primary Window (the hosting window)."""
    with dpg.window(tag=self._primary_window_ref):
      pass
    dpg.create_viewport(title="Intelligent Agent Playground")

  def _setup_menu_bar(self):
    """Configure the primary window's menu bar."""
    with dpg.viewport_menu_bar():
      with dpg.menu(label="Simulations"):
        dpg.add_menu_item(label="Pulsing Circle", callback=self._launch_simulation, tag=self._menu_items['sims']['pulsing_circle_sim'])
        dpg.add_menu_item(label="Single Agent", callback=self._launch_simulation, tag=self._menu_items['sims']['launch_single_agent_sim'])

  def _launch_simulation(self, sender, item_data, user_data):
    if self._active_simulation is not None:
      """Only allow one active simulation at a time."""
      return

    self._active_simulation = self._select_simulation(sender)
    
    if self._active_simulation is not None:
      self._active_simulation.primary_window = self._primary_window_ref
      self._active_simulation.attach(self)
      self._active_simulation.launch()

  def _select_simulation(self, menu_item_ref: Union[int, str]) -> Optional[Simulation]:
    simulation: Optional[Simulation] = None
    if menu_item_ref is self._menu_items['sims']['launch_single_agent_sim']:
      simulation = SingleAgentSimulation()
    elif menu_item_ref is self._menu_items['sims']['pulsing_circle_sim']:
      simulation = PulsingCircleSim()
    return simulation