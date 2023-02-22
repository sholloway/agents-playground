from __future__ import annotations

import os
from typing import Any, cast


import dearpygui.dearpygui as dpg

from agents_playground.app.create_sim_wizard import CreateSimWizard
from agents_playground.core.constants import DEFAULT_FONT_SIZE

from agents_playground.core.observe import Observable, Observer
from agents_playground.core.simulation import Simulation
from agents_playground.project.extensions import simulation_extensions
from agents_playground.project.rules.project_loader import ProjectLoader
from agents_playground.project.project_loader_error import ProjectLoaderError
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
    self.__active_simulation: Simulation | None = None

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
  # DPG Debug Windows
    # dpg.show_metrics()
    dpg.show_item_registry()
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
  def active_simulation(self) -> Simulation | None:
    return self.__active_simulation

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
        if self.active_simulation:
          self.active_simulation.handle_keyboard_events(key_code)

  def __enable_windows_context(self) -> None:
    dpg.create_context()

  def __configure_primary_window(self):
    """Configure the Primary Window (the hosting window)."""
    logger.info('PlaygroundApp: Configuring primary window')
    with dpg.window(tag=self.__primary_window_ref):
      dpg.bind_font(font = 'hack-nerd-font')
      # dpg.bind_font(font = 'fira-code-font')

    dpg.create_viewport(title="Intelligent Agent Playground", vsync=True)

  def __setup_menu_bar(self):
    """Configure the primary window's menu bar."""
    logger.info('PlaygroundApp: Configuring the primary window\'s menu bar.')
    # TODO Put this in a TOML file?
    with dpg.viewport_menu_bar():
      with dpg.menu(label="Simulations"):
        dpg.add_menu_item(label="New", callback=self._launch_new_sim_wizard)
        dpg.add_menu_item(label="Open", callback=self._open_sim)
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
  
  def _launch_new_sim_wizard(self) -> None:
    wizard = CreateSimWizard()
    wizard.launch()

  def _open_sim(self) -> None:
    if self.__active_simulation is None:
      with dpg.file_dialog(
        label               = "Open Simulation",
        modal               = True, 
        directory_selector  = True, 
        callback            = self._handle_sim_selected,
        width               = 750,
        height              = 400
      ):
        pass

  def _handle_sim_selected(self, sender, app_data):
    """
    The steps that need to happen here are:
    1. Validate the project rules.
    2. Load the project module.
    3. Somehow register all of the module's extension code (renderers, tasks, entities, etc..).
    4. Create a Simulation instance using the project's scene.toml file.
    5. Activate the primary window.
    6. Attach to the simulation.
    7. Launch the simulation instance.
    """

    print(app_data)
    
    if len(app_data['selections']) == 1:
      project_path = app_data['file_path_name']
      module_name = project_path.split('/')[-1]
      pl = ProjectLoader()
      try:
        pl.validate(module_name, project_path)   
        pl.load(module_name, project_path)
        se = simulation_extensions()

        scene_file: str = os.path.join(project_path, 'scene.toml')
        self.__active_simulation = Simulation(scene_file)
        self.__active_simulation.primary_window = self.__primary_window_ref
        self.__active_simulation.attach(self)
        self.__active_simulation.launch()
      except ProjectLoaderError as e:
        print(e)

"""
TODO
- Bug: When a project is loaded a second time, the registration decorators 
  aren't running. I imagine this is because the module is already 'loaded'. When
  a sim shuts down I think I need to remove it from sys.modules[module_name].
  It's probably more nuanced than that.

  Getting "ModuleNotFoundError: spec not found for the module 'my_sim'" when trying
  to reload the module. The docs are super helpful. Look at the code for importlib.reload
  to se how this is throwing the error.
  /nix/store/13gh1aq94wdlhlrvn6q0q8giw0az6wl9-python3-3.11.1/lib/python3.11/importlib/__init__.py", line 168, in reload

  I may be going about this all wrong. importlib is for importing modules or rather single files.
  The pkgutils provides methods for importing packages. This may be a better approach.

- Actually make it work. ;)
- Consider using a template engine for the TOML creation. 
  Although, I prefer to not add any more dependencies.
"""