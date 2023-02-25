from __future__ import annotations
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Callable, List, Tuple

import dearpygui.dearpygui as dpg

from agents_playground.simulation.tag import Tag

@dataclass
class CreateSimWizardUIComponents:
  new_simulation_window: Tag
  project_name_input: Tag
  simulation_title_input: Tag
  simulation_description_input: Tag
  select_directory_button: Tag
  selected_directory_display: Tag
  
  def __init__(self, generate_uuid: Callable[..., Tag]) -> None:
    self.new_simulation_window        = generate_uuid()
    self.project_name_input           = generate_uuid()
    self.simulation_title_input       = generate_uuid()
    self.simulation_description_input = generate_uuid()
    self.select_directory_button      = generate_uuid()
    self.selected_directory_display   = generate_uuid()

TOOL_TIP_WIDTH: int        = 350
WIZARD_WINDOW_WIDTH: int   = 518
WIZARD_WINDOW_HEIGHT: int  = 260

def find_centered_window_position(
  parent_width: int, 
  parent_height: int, 
  child_width: int, 
  child_height: int
) -> Tuple[int]:
  return (
    parent_width/2 - child_width/2,
    parent_height/2 - child_height/2
  )

class CreateSimWizard:
  """
  A UI based wizard for creating a simulation. It is designed as a singleton
  to prevent multiple instance being open at the same time. 
  This is redundant when the window is launched as a modal.
  """
  _instance: CreateSimWizard | None = None
  
  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(CreateSimWizard, cls).__new__(cls)
      cls._ui_components = CreateSimWizardUIComponents(dpg.generate_uuid)
      cls._active = False
      cls._project_parent_directory: str | None = None
    return cls._instance
  
  def launch(self) -> None:
    if not self._active:
      self._active = True
      if dpg.does_item_exist(self._ui_components.new_simulation_window):
        wizard_position = find_centered_window_position(
          dpg.get_viewport_width(), 
          dpg.get_viewport_height(), 
          WIZARD_WINDOW_WIDTH, 
          WIZARD_WINDOW_HEIGHT
        )
        dpg.configure_item(self._ui_components.new_simulation_window, pos = wizard_position)
        dpg.configure_item(self._ui_components.new_simulation_window, show = True)

      else:
        self._build_new_sim_window()

  def _build_new_sim_window(self) -> None:
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
      on_close  = self._handle_closing_new_sim_window
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
        dpg.add_text('Pick the directory that will contain the project. A new directory will be created here.', wrap=TOOL_TIP_WIDTH)

      dpg.add_button(label="Create Simulation", callback=self._create_simulation)

  def _handle_closing_new_sim_window(self) -> None:
    self._active = False
    dpg.configure_item(self._ui_components.new_simulation_window, show = False)
    self._reset_new_sim_inputs()

  def _reset_new_sim_inputs(self) -> None:
    dpg.set_value(self._ui_components.project_name_input, '')
    dpg.set_value(self._ui_components.simulation_title_input, '')
    dpg.set_value(self._ui_components.simulation_description_input, '')
    dpg.set_value(self._ui_components.selected_directory_display, '')
    self._project_parent_directory = None 

  def _add_text_input(self, tag, label, tooltip, hint = '', multiline=False, no_spaces=False) -> None:
    with dpg.table_row():
      dpg.add_text(label)
      dpg.add_input_text(tag=tag, multiline=multiline, width = 400, hint=hint, no_spaces=no_spaces)
      if tooltip:
        with dpg.tooltip(parent=tag):
          dpg.add_text(tooltip, wrap=TOOL_TIP_WIDTH)

  def _create_simulation(self) -> None:
    """Create the simulation and close the window."""
    # 1. Get all of the input values
    project_name: str     = dpg.get_value(self._ui_components.project_name_input)
    sim_title: str        = dpg.get_value(self._ui_components.simulation_title_input)
    sim_description: str  = dpg.get_value(self._ui_components.simulation_description_input)

    try:
      # 2. Perform validations
      validate_required_str(project_name, 'Project Name must be specified.')
      validate_required_str(sim_title, 'Simulation Title must be specified.')
      validate_required_str(sim_description, 'Simulation Description must be specified.')
      validate_required_str(self._project_parent_directory, "The project's parent directory must be specified.")

      # 3. Create the new project

      # 4. Close the window
      dpg.configure_item(self._ui_components.new_simulation_window, show=False)
      dpg.delete_item(self._ui_components.new_simulation_window)
      self._active = False
    except NewProjectValidationError as e:
      print(e)

  def _select_directory(self) -> None:
    dpg.add_file_dialog(
      label               = "Pick a Project Home",
      modal               = True, 
      directory_selector  = True, 
      callback            = self._handle_directory_selected,
      width               = 750,
      height              = 400,
      default_path        = os.path.join(Path.home(), 'Documents/Code') #TODO: Need a setting for the user's preferred path.
    )
    
  def _handle_directory_selected(self, sender, app_data) -> None:
    self._project_parent_directory = app_data['file_path_name']
    dpg.set_value(item=self._ui_components.selected_directory_display, value=self._project_parent_directory)
    self._ui_components.selected_directory_display

def validate_required_str(input_value: str | None, error_msg: str) -> None:
  if input_value is None or input_value.strip() == '':
    raise NewProjectValidationError(error_msg)
  
class NewProjectValidationError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)