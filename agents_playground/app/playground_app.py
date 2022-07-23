from typing import Any, Union

import dearpygui.dearpygui as dpg

from agents_playground.core.observe import Observable, Observer
from agents_playground.core.simulation import Simulation
from agents_playground.core.simulation_old import SimulationOld
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger
from agents_playground.simulation.sim_events import SimulationEvents

logger = get_default_logger()
class PlaygroundApp(Observer):
  def __init__(self) -> None:
    logger.info('PlaygroundApp: Initializing')
    self._enable_windows_context()
    self._primary_window_ref = dpg.generate_uuid()
    self._menu_items = {
      'sims': {
        'pulsing_circle_sim': dpg.generate_uuid(),
        'launch_toml_sim': dpg.generate_uuid()
      }
    }
    self._active_simulation: Union[SimulationOld, Observable, None] = None

  def launch(self) -> None:
    """Run the application"""
    logger.info('PlaygroundApp: Launching')
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
    logger.info('PlaygroundApp: Update message received.')
    if msg == SimulationEvents.WINDOW_CLOSED.value and self._active_simulation is not None:
      self._active_simulation.detach(self)
      self._active_simulation = None

  @property
  def active_simulation(self) -> Union[SimulationOld, Observable, None]:
    return self._active_simulation

  def _enable_windows_context(self) -> None:
    dpg.create_context()

  def _configure_primary_window(self):
    """Configure the Primary Window (the hosting window)."""
    logger.info('PlaygroundApp: Configuring primary window')
    with dpg.window(tag=self._primary_window_ref):
      pass
    dpg.create_viewport(title="Intelligent Agent Playground", vsync=True)

  def _setup_menu_bar(self):
    """Configure the primary window's menu bar."""
    logger.info('PlaygroundApp: Configuring the primary window\'s menu bar.')
    # TODO Put this in a TOML file?
    with dpg.viewport_menu_bar():
      with dpg.menu(label="Simulations"):
        dpg.add_menu_item(label="Pulsing Circle", callback=self._launch_simulation, tag=self._menu_items['sims']['pulsing_circle_sim'], user_data='agents_playground/sims/pulsing_circle_sim.toml')
        dpg.add_menu_item(label="TOML Scene", callback=self._launch_simulation, tag=self._menu_items['sims']['launch_toml_sim'], user_data='agents_playground/sims/simple_movement.toml')

  def _launch_simulation(self, sender: Tag, item_data: Any, user_data: Any):
    logger.info('PlaygroundApp: Launching simulation.')
    """Only allow one active simulation at a time."""
    if self._active_simulation is None:
      self._active_simulation = self._build_simulation(user_data)
      self._active_simulation.primary_window = self._primary_window_ref
      self._active_simulation.attach(self)
      self._active_simulation.launch()

  def _build_simulation(self, user_data: Any) -> Simulation:
    return Simulation(user_data)