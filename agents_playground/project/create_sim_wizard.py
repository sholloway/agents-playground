from __future__ import annotations

import os
from pathlib import Path
from typing import  List

import dearpygui.dearpygui as dpg
from agents_playground.project.constants import WIZARD_WINDOW_HEIGHT, WIZARD_WINDOW_WIDTH
from agents_playground.project.create_sim_wizard_ui_components import CreateSimWizardUIComponents
from agents_playground.project.input_processors import InputProcessor, TextFieldProcessor, TextInputProcessor
from agents_playground.project.new_project_validation_error import NewProjectValidationError
from agents_playground.project.new_sim_window import NewSimWindow
from agents_playground.project.project_builder import ProjectBuilder
from agents_playground.project.project_template_options import ProjectTemplateOptions


from agents_playground.ui.utilities import create_error_window, create_success_window, find_centered_window_position

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
      cls._project_template_options = ProjectTemplateOptions()
      cls._input_processors: List[InputProcessor] = [
        TextInputProcessor(cls._ui_components.project_name_input, 'Project Name must be specified.', 'project_name'),
        TextInputProcessor(cls._ui_components.simulation_title_input, 'Simulation Title must be specified.', 'simulation_title'),
        TextInputProcessor(cls._ui_components.simulation_description_input, 'Simulation Description must be specified.', 'simulation_description'),
        TextFieldProcessor(cls._instance, '_project_parent_directory', "The project's parent directory must be specified.", 'project_parent_directory')
      ]
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
    NewSimWindow(
      self._ui_components, 
      on_close          = self._handle_closing_new_sim_window,
      select_dir        = self._select_directory,
      create_simulation = self._create_simulation
    ).build_window()

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

  def _create_simulation(self) -> None:
    """Create the simulation and close the window."""
    try:
      ProjectBuilder().build(self._project_template_options, self._input_processors)
      self._close_window()
      self._popup_success_msg()
    except NewProjectValidationError as e:
      self._handle_input_error(e.args[0])

  def _handle_input_error(self, error: NewProjectValidationError) -> None:
    create_error_window(
      'Project Input Error', 
      repr(error))

  def _select_directory(self) -> None:
    dpg.add_file_dialog(
      label               = "Pick a Project Home",
      modal               = True, 
      directory_selector  = True, 
      callback            = self._handle_directory_selected,
      width               = 750,
      height              = 400,
      default_path        = os.path.join(Path.home(), 'Documents') #TODO: Need a setting for the user's preferred path.
    )
    
  def _handle_directory_selected(self, sender, app_data) -> None:
    if len(app_data['selections']) == 1:
      self._project_parent_directory = app_data['file_path_name']
      dpg.set_value(item=self._ui_components.selected_directory_display, value=self._project_parent_directory)
      self._ui_components.selected_directory_display
    else:
      create_error_window(
        'Directory Selection Error', 
        'You may only select a single directory for the project to live in.')
  
  def _close_window(self) -> None:
    dpg.configure_item(self._ui_components.new_simulation_window, show=False)
    dpg.delete_item(self._ui_components.new_simulation_window)
    self._active = False

  def _popup_success_msg(self) -> None:
    new_project_dir = os.path.join(self._project_template_options.project_parent_directory, self._project_template_options.project_name)
    create_success_window('Success', f'New project created at {new_project_dir}')