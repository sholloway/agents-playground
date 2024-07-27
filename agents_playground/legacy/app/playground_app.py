from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List, cast

import dearpygui.dearpygui as dpg

from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.legacy.project.create_sim_wizard import CreateSimWizard
from agents_playground.core.constants import DEFAULT_FONT_SIZE

from agents_playground.core.observe import Observable, Observer
from agents_playground.core.simulation import Simulation
from agents_playground.legacy.project.extensions import simulation_extensions
from agents_playground.legacy.project.rules.project_loader import ProjectLoader
from agents_playground.legacy.project.project_loader_error import ProjectLoaderError
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger
from agents_playground.simulation.sim_events import SimulationEvents
from agents_playground.ui.utilities import create_error_window

logger = get_default_logger()
class PlaygroundApp(Observer):
  def __init__(self) -> None:
    logger.info('PlaygroundApp: Initializing')
    self._enable_windows_context()
    self._primary_window_ref = dpg.generate_uuid()
    self._menu_items = {
      'sims': {
        'pulsing_circle_sim': dpg.generate_uuid(),
        'launch_toml_sim': dpg.generate_uuid(),
        'our_town': dpg.generate_uuid()
      }
    }
    self._active_simulation: Maybe[Simulation] = Nothing()

  def launch(self) -> None:
    """Run the application"""
    logger.info('PlaygroundApp: Launching')

    self._setup_fonts()
    
    # Fooling around with listening to the keyboard
    with dpg.handler_registry():
      dpg.add_key_down_handler(callback = self._key_down)
      dpg.add_key_release_handler(callback = self._key_released)
      dpg.add_key_press_handler(callback = self._key_pressed)
    
    self._configure_primary_window()
    self._setup_menu_bar()
  # DPG Debug Windows
    # dpg.show_metrics()
    # dpg.show_item_registry()
    # dpg.show_font_manager()
    dpg.setup_dearpygui() # Assign the viewport
    dpg.show_viewport(maximized=True)
    dpg.set_primary_window(self._primary_window_ref, True)
    dpg.set_exit_callback(self._on_close)
    dpg.maximize_viewport()
    dpg.start_dearpygui() 
    dpg.destroy_context()

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""   
    logger.info('PlaygroundApp: Update message received.')
    if msg == SimulationEvents.WINDOW_CLOSED.value and self._active_simulation.is_something():
      self._active_simulation.unwrap().detach(self)
      self._active_simulation = Nothing()

  @property
  def active_simulation(self) -> Maybe[Simulation]:
    return self._active_simulation

  def _setup_fonts(self) -> None:
    self._register_font('agents_playground/fonts/Hack Regular Nerd Font Complete.ttf', 'hack-nerd-font')
    # self._register_font('agents_playground/fonts/Fira Code Regular Nerd Font Complete.ttf', 'fira-code-font')
 
  def _register_font(self, relative_path_to_font: str, font_alias: str) -> None:
      with dpg.font_registry():
        font_abs_path = os.path.abspath(relative_path_to_font)
        with dpg.font(
          file = font_abs_path,
          size = DEFAULT_FONT_SIZE,
          tag = font_alias
        ):
            # add the default font range
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)

            # add specific glyphs
            dpg.add_font_chars(
                [
                    0x2588, # Block
                    0xE285, # Thick >
                    0xE73C, # Python Logo
                    0xF120, # Terminal Prompt
                    0xFCB5, # Terminal Prompt Alternative
                    0xF177, # <-
                    0xF178, # ->
                    0x2260, # !=
                    0x2264, # <=
                    0x2265, # >=
                    0x221A, # sqrt
                    0x221E # Infinity
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
        if self.active_simulation.is_something():
          self.active_simulation.unwrap().handle_keyboard_events(key_code)

  def _enable_windows_context(self) -> None:
    dpg.create_context()

  def _configure_primary_window(self):
    """Configure the Primary Window (the hosting window)."""
    logger.info('PlaygroundApp: Configuring primary window')
    with dpg.window(tag=self._primary_window_ref):
      dpg.bind_font(font = 'hack-nerd-font')
      # dpg.bind_font(font = 'fira-code-font')

    dpg.create_viewport(title="Intelligent Agent Playground", vsync=True)

  def _setup_menu_bar(self):
    """Configure the primary window's menu bar."""
    logger.info('PlaygroundApp: Configuring the primary window\'s menu bar.')
    # TODO Put this in a TOML file?
    with dpg.viewport_menu_bar():
      with dpg.menu(label="Simulations"):
        dpg.add_menu_item(label="New", callback=self._launch_new_sim_wizard)
        dpg.add_menu_item(label="Open", callback=self._open_sim)
        # dpg.add_menu_item(label="Pulsing Circle", callback=self.__launch_simulation, tag=self.__menu_items['sims']['pulsing_circle_sim'], user_data='agents_playground/sims/pulsing_circle_sim.toml')
        # dpg.add_menu_item(label="Example TOML Scene", callback=self._launch_simulation, tag=self._menu_items['sims']['launch_toml_sim'], user_data='agents_playground/sims/simple_movement.toml')
        # dpg.add_menu_item(label="Our Town", callback=self._launch_simulation, tag=self._menu_items['sims']['our_town'], user_data='agents_playground/sims/our_town.toml')

  def _launch_simulation(self, sender: Tag, item_data: Any, user_data: Any):
    logger.info('PlaygroundApp: Launching simulation.')
    """Only allow one active simulation at a time."""
    if not self._active_simulation.is_something():
      sim: Simulation = self._build_simulation(user_data)
      self._active_simulation = Something(sim)
      sim.primary_window = self._primary_window_ref
      sim.attach(self)
      sim.launch()

  def _build_simulation(self, user_data: Any) -> Simulation:
    return Simulation(user_data)

  def _on_close(self) -> None:
    logger.info('Playground App: On close called.')
    if self._active_simulation is not None:
      cast(Simulation, self._active_simulation).shutdown()
  
  def _launch_new_sim_wizard(self) -> None:
    if self._active_simulation is None:
      wizard = CreateSimWizard()
      wizard.launch()

  def _open_sim(self) -> None:
    if self._active_simulation is None:
      dpg.add_file_dialog(
        label               = "Open Simulation",
        modal               = True, 
        directory_selector  = True, 
        callback            = self._handle_sim_selected,
        width               = 750,
        height              = 400,
        default_path        = os.path.join(Path.home(), 'Documents/Code') #TODO: Need a setting for the user's preferred path.
      )

  def _handle_sim_selected(self, sender, app_data):
    if len(app_data['selections']) == 1:
      module_name = os.path.basename(app_data['file_path_name'])
      project_path = os.path.join(app_data['file_path_name'], module_name)
      pl = ProjectLoader()
      try:
        pl.validate(module_name, project_path)   
        pl.load_or_reload(module_name, project_path)
        scene_file: str = os.path.join(project_path, 'scene.toml')
        sim: Simulation = self._build_simulation(scene_file)
        self._active_simulation = Something(sim)
        sim.primary_window = self._primary_window_ref
        sim.attach(self)
        sim.launch()
      except ProjectLoaderError as e:
        print(e)
        create_error_window(
          'Project Validation Error', 
          repr(e))
    else:  
      create_error_window(
        'Project Selection Error', 
        'You may only select a single project to load.')