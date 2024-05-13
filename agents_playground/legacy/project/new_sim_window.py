from typing import Callable
import dearpygui.dearpygui as dpg

from agents_playground.legacy.project.constants import TOOL_TIP_WIDTH, WIZARD_WINDOW_HEIGHT, WIZARD_WINDOW_WIDTH
from agents_playground.legacy.project.create_sim_wizard_ui_components import CreateSimWizardUIComponents
from agents_playground.ui.utilities import find_centered_window_position

class NewSimWindow:
  def __init__(
    self, 
    ui_components: CreateSimWizardUIComponents, 
    on_close: Callable, 
    select_dir: Callable,
    create_simulation: Callable
  ) -> None:
    self._ui_components = ui_components
    self._on_close = on_close
    self._select_directory = select_dir
    self._create_simulation = create_simulation

  def build_window(self) -> None:
    wizard_position = find_centered_window_position(
      dpg.get_viewport_width(), 
      dpg.get_viewport_height(), 
      WIZARD_WINDOW_WIDTH, 
      WIZARD_WINDOW_HEIGHT
    )
    with dpg.window(
      tag       = self._ui_components.new_simulation_window, 
      label     = "Create a New Simulation", 
      width     = WIZARD_WINDOW_WIDTH, 
      height    = WIZARD_WINDOW_HEIGHT,
      pos       = wizard_position,
      no_resize = True,
      on_close  = self._on_close
    ):
      with dpg.table(header_row=False):
        dpg.add_table_column(width_fixed=True)
        dpg.add_table_column(width_stretch=True, init_width_or_weight=0.0)

        self._add_text_input(
          tag       = self._ui_components.project_name_input,
          label     = "Name", 
          tooltip   = "Assign a unique name for the simulation. This is the name of the simulation file.",
          hint      = "Example: my_simulation",
          no_spaces = True
        )

        self._add_text_input(
          tag     = self._ui_components.simulation_title_input,
          label   = "Title", 
          tooltip = "Assign a unique title for the simulation. This will be displayed in the Simulation menu.",
          hint    = "Example: My Simulation"
        )

        self._add_text_input(
          tag     = self._ui_components.simulation_description_input,
          label   = "Description", 
          tooltip = "Describe what the simulation does. This will be displayed in the Simulation window.",
          multiline = True
        )
    
        with dpg.table_row():
          dpg.add_button(
            tag=self._ui_components.select_directory_button,  
            label="Select Directory", 
            callback=self._select_directory
          )
          dpg.add_text(default_value='', tag=self._ui_components.selected_directory_display)

      with dpg.tooltip(parent=self._ui_components.select_directory_button):
        dpg.add_text('Pick the directory that will contain the project. A new directory will be created here.', wrap = TOOL_TIP_WIDTH)

      dpg.add_button(label="Create Simulation", callback=self._create_simulation)

  def _add_text_input(self, tag, label, tooltip, hint = '', multiline=False, no_spaces=False) -> None:
    with dpg.table_row():
      dpg.add_text(label)
      dpg.add_input_text(tag=tag, multiline=multiline, width = 400, hint=hint, no_spaces=no_spaces)
      if tooltip:
        with dpg.tooltip(parent=tag):
          dpg.add_text(tooltip, wrap=TOOL_TIP_WIDTH)

  