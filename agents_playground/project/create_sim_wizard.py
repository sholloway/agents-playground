from __future__ import annotations
from dataclasses import dataclass, field
import os
from pathlib import Path
import shutil
from string import Template
from typing import Any, Callable, Dict, List

import dearpygui.dearpygui as dpg
from agents_playground.project.input_processors import InputProcessor, TextFieldProcessor, TextInputProcessor
from agents_playground.project.new_project_validation_error import NewProjectValidationError
from agents_playground.project.project_template_options import ProjectTemplateOptions

from agents_playground.simulation.tag import Tag
from agents_playground.ui.utilities import create_error_window, create_success_window, find_centered_window_position

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

def populate_template(path_to_template: Path, path_to_target: Path, template_inputs: dict[str, Any]) -> None:
  scene_template: str = path_to_template.read_text()
  scene_file = Template(scene_template).substitute(template_inputs)
  path_to_target.write_text(scene_file)

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
    try:
      self._process_form_inputs()
      self._validate_form_inputs()
      self._prevent_over_writing_existing_directories()
      self._copy_template_directory()
      self._rename_pkg_directory()
      self._generate_project_files()
      self._copy_wheel()
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
      
  def _process_form_inputs(self) -> None:
    [input.grab_value(self._project_template_options) for input in self._input_processors]

  def _validate_form_inputs(self) -> None: 
    [input.validate() for input in self._input_processors]

  def _prevent_over_writing_existing_directories(self) -> None:
    new_project_dir = os.path.join(self._project_template_options.project_parent_directory, self._project_template_options.project_name)
    if os.path.isdir(new_project_dir):
      raise NewProjectValidationError(f'Cannot create the new project. The directory {new_project_dir} already exists. Please specify a different project name.')
    
  def _copy_template_directory(self) -> None:
    new_project_dir = os.path.join(self._project_template_options.project_parent_directory, self._project_template_options.project_name)
    template_dir = os.path.join(Path.cwd(), 'agents_playground/templates/new_project')
    shutil.copytree(template_dir, new_project_dir)

  def _rename_pkg_directory(self) -> None:
    package_dir = os.path.join(self._project_template_options.project_parent_directory, self._project_template_options.project_name, 'project_pkg')
    project_pkg_dir = os.path.join(self._project_template_options.project_parent_directory, self._project_template_options.project_name, self._project_template_options.project_name)
    Path(package_dir).rename(project_pkg_dir)

  def _generate_project_files(self) -> None:
    template_inputs = vars(self._project_template_options)
    template_inputs['project_pkg'] = self._project_template_options.project_name
    new_project_dir = os.path.join(self._project_template_options.project_parent_directory, self._project_template_options.project_name)

    # Handle Scene File
    scene_template_path: Path = Path(os.path.join(Path.cwd(), 'agents_playground/templates/base_files/scene.toml'))
    scene_file_path: Path = Path(os.path.join(new_project_dir, self._project_template_options.project_name, 'scene.toml'))
    populate_template(scene_template_path, scene_file_path, template_inputs)

    # Handle __init__.py
    init_template_path: Path = Path(os.path.join(Path.cwd(), 'agents_playground/templates/base_files/__init__.py'))
    init_file_path: Path = Path(os.path.join(new_project_dir, self._project_template_options.project_name, '__init__.py'))
    populate_template(init_template_path, init_file_path, template_inputs)

    # Handle scene.py
    scene_py_template_path: Path = Path(os.path.join(Path.cwd(), 'agents_playground/templates/base_files/scene.py'))
    scene_py_file_path: Path = Path(os.path.join(new_project_dir, self._project_template_options.project_name, 'scene.py'))
    populate_template(scene_py_template_path, scene_py_file_path, template_inputs)
    
    # Handle simulation_test.py
    simulation_test_template_path: Path = Path(os.path.join(Path.cwd(), 'agents_playground/templates/base_files/simulation_test.py'))
    simulation_test_file_path: Path = Path(os.path.join(new_project_dir, 'tests', 'simulation_test.py'))
    populate_template(simulation_test_template_path, simulation_test_file_path, template_inputs)

  def _copy_wheel(self) -> None:
    """Note
    This is a temporary fix. The idea is to ultimately have the engine available 
    on pypi.org as a Python package. The created project would then automatically 
    install the package when the user runs the projects setup for doing unit testing.
    """
    engine_pkg = 'agents_playground-0.1.0-py3-none-any.whl'
    wheel_path: Path = Path(os.path.join(Path.cwd(), 'dist', engine_pkg))
    new_project_dir: Path = Path(os.path.join(self._project_template_options.project_parent_directory, self._project_template_options.project_name))
    destination_path: Path = Path(os.path.join(new_project_dir, 'libs', engine_pkg))
    shutil.copyfile(wheel_path, destination_path)

  def _close_window(self) -> None:
    dpg.configure_item(self._ui_components.new_simulation_window, show=False)
    dpg.delete_item(self._ui_components.new_simulation_window)
    self._active = False

  def _popup_success_msg(self) -> None:
    new_project_dir = os.path.join(self._project_template_options.project_parent_directory, self._project_template_options.project_name)
    create_success_window('Success', f'New project created at {new_project_dir}')