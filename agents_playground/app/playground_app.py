from __future__ import annotations
import os
from typing import Any, Union, cast
import dearpygui.dearpygui as dpg
from agents_playground.core.constants import DEFAULT_FONT_SIZE

from agents_playground.core.observe import Observable, Observer
from agents_playground.core.simulation import Simulation
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger
from agents_playground.simulation.sim_events import SimulationEvents

logger = get_default_logger()
class PlaygroundApp(Observer):
  def __init__(self) -> None:
    logger.info('PlaygroundApp: Initializing')
    self.__enable_windows_context()
    self.__primary_window_ref = dpg.generate_uuid()
    self.__menu_items = {
      'sims': {
        'pulsing_circle_sim': dpg.generate_uuid(),
        'launch_toml_sim': dpg.generate_uuid(),
        'our_town': dpg.generate_uuid()
      }
    }
    self.__active_simulation: Simulation | Observable | None = None

  def launch(self) -> None:
    """Run the application"""
    logger.info('PlaygroundApp: Launching')

    self._setup_fonts()
    
    # Fooling around with listening to the keyboard
    with dpg.handler_registry():
      dpg.add_key_down_handler(callback = self._key_down)
      dpg.add_key_release_handler(callback = self._key_released)
      dpg.add_key_press_handler(callback = self._key_pressed)
    
    self.__configure_primary_window()
    self.__setup_menu_bar()
  # DPG Debug Windows_run_sim_toggle_btn_clicked
    # dpg.show_metrics()
    # dpg.show_item_registry()
    # dpg.show_font_manager()
    dpg.setup_dearpygui() # Assign the viewport
    dpg.show_viewport(maximized=True)
    dpg.set_primary_window(self.__primary_window_ref, True)
    dpg.set_exit_callback(self.__on_close)
    dpg.maximize_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""   
    logger.info('PlaygroundApp: Update message received.')
    if msg == SimulationEvents.WINDOW_CLOSED.value and self.__active_simulation is not None:
      self.__active_simulation.detach(self)
      self.__active_simulation = None

  @property
  def active_simulation(self) -> Simulation | Observable | None:
    return self.__active_simulation

  def _setup_fonts(self) -> None:
    with dpg.font_registry():
      hack_nerd_reg_path = os.path.abspath('agents_playground/fonts/Hack Regular Nerd Font Complete.ttf')
      with dpg.font(
        file = hack_nerd_reg_path,
        size = DEFAULT_FONT_SIZE,
        tag = 'hack-nerd-font'
      ):
        # add the default font range
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)

         # add specific glyphs
        dpg.add_font_chars(
          [
            0x2588, # Block
            0xE285, # Thick >
            0xE73C  # Python Logo
          ]
        )
      
  def _key_down(self, **data) -> None:
    pass
  
  def _key_released(self, **data) -> None:
    pass
  
  def _key_pressed(self, sender, key_code) -> None:
    # dpg.is_focus/selected
    match key_code:
      case dpg.mvKey_Shift | dpg.mvKey_Capital:
        pass
      case _:
        if self.active_simulation:
          self.active_simulation.handle_keyboard_events(key_code)

  def __enable_windows_context(self) -> None:
    dpg.create_context()

  def __configure_primary_window(self):
    """Configure the Primary Window (the hosting window)."""
    logger.info('PlaygroundApp: Configuring primary window')
    with dpg.window(tag=self.__primary_window_ref):
      dpg.bind_font(font = 'hack-nerd-font')

    dpg.create_viewport(title="Intelligent Agent Playground", vsync=True)

  def __setup_menu_bar(self):
    """Configure the primary window's menu bar."""
    logger.info('PlaygroundApp: Configuring the primary window\'s menu bar.')
    # TODO Put this in a TOML file?
    with dpg.viewport_menu_bar():
      with dpg.menu(label="Simulations"):
        dpg.add_menu_item(label="Pulsing Circle", callback=self.__launch_simulation, tag=self.__menu_items['sims']['pulsing_circle_sim'], user_data='agents_playground/sims/pulsing_circle_sim.toml')
        dpg.add_menu_item(label="Example TOML Scene", callback=self.__launch_simulation, tag=self.__menu_items['sims']['launch_toml_sim'], user_data='agents_playground/sims/simple_movement.toml')
        dpg.add_menu_item(label="Our Town", callback=self.__launch_simulation, tag=self.__menu_items['sims']['our_town'], user_data='agents_playground/sims/our_town.toml')

  def __launch_simulation(self, sender: Tag, item_data: Any, user_data: Any):
    logger.info('PlaygroundApp: Launching simulation.')
    """Only allow one active simulation at a time."""
    if self.__active_simulation is None:
      self.__active_simulation = self.__build_simulation(user_data)
      self.__active_simulation.primary_window = self.__primary_window_ref
      self.__active_simulation.attach(self)
      self.__active_simulation.launch()

  def __build_simulation(self, user_data: Any) -> Simulation:
    return Simulation(user_data)

  def __on_close(self) -> None:
    logger.info('Playground App: On close called.')
    if self.__active_simulation is not None:
      cast(Simulation, self.__active_simulation).shutdown()