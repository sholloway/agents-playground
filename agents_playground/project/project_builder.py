
import os
from pathlib import Path
import shutil
from string import Template
from typing import Any, List, NamedTuple

from agents_playground.project.input_processors import InputProcessor
from agents_playground.project.new_project_validation_error import NewProjectValidationError
from agents_playground.project.project_template_options import ProjectTemplateOptions

def populate_template(path_to_template: Path, path_to_target: Path, template_inputs: dict[str, Any]) -> None:
  scene_template: str = path_to_template.read_text()
  scene_file = Template(scene_template).substitute(template_inputs)
  path_to_target.write_text(scene_file)

class TemplateFile(NamedTuple):
  template_name: str
  template_location: str
  target_location: str

# Note: All of the template data can use $var and ${var} for dynamic population.
TEMPLATES = [
  TemplateFile('scene.toml',         'agents_playground/templates/base_files', '$project_pkg'),
  TemplateFile('__init__.py',        'agents_playground/templates/base_files', '$project_pkg'),
  TemplateFile('scene.py',           'agents_playground/templates/base_files', '$project_pkg'),
  TemplateFile('simulation_test.py', 'agents_playground/templates/base_files', 'tests')
]
class ProjectBuilder:  
  def build(self, project_options: ProjectTemplateOptions, input_processors: List[InputProcessor]) -> None:
    self._process_form_inputs(project_options, input_processors)
    self._validate_form_inputs(input_processors)
    self._prevent_over_writing_existing_directories(project_options)
    self._copy_template_directory(project_options)
    self._rename_pkg_directory(project_options)
    self._generate_project_files(project_options)
    self._copy_wheel(project_options)

  def _process_form_inputs(self, project_options: ProjectTemplateOptions, input_processors: List[InputProcessor]) -> None:
    [input.grab_value(project_options) for input in input_processors]

  def _validate_form_inputs(self, input_processors: List[InputProcessor]) -> None: 
    [input.validate() for input in input_processors]

  def _prevent_over_writing_existing_directories(self, project_options: ProjectTemplateOptions) -> None:
    new_project_dir = os.path.join(project_options.project_parent_directory, project_options.project_name)
    if os.path.isdir(new_project_dir):
      error_msg = f'Cannot create the new project. The directory {new_project_dir} already exists. Please specify a different project name.'
      raise NewProjectValidationError(error_msg)

  def _copy_template_directory(self, project_options: ProjectTemplateOptions) -> None:
    new_project_dir = os.path.join(project_options.project_parent_directory, project_options.project_name)
    template_dir = os.path.join(Path.cwd(), 'agents_playground/templates/new_project')
    shutil.copytree(template_dir, new_project_dir)

  def _rename_pkg_directory(self, project_options: ProjectTemplateOptions) -> None:
    package_dir = os.path.join(project_options.project_parent_directory, project_options.project_name, 'project_pkg')
    project_pkg_dir = os.path.join(project_options.project_parent_directory, project_options.project_name, project_options.project_name)
    Path(package_dir).rename(project_pkg_dir)

  def _generate_project_files(self, project_options: ProjectTemplateOptions) -> None:
    template_inputs = vars(project_options)
    template_inputs['project_pkg'] = project_options.project_name
    new_project_dir = os.path.join(project_options.project_parent_directory, project_options.project_name)

    for template in TEMPLATES:
      hydrated_template_location: str = Template(template.template_location).substitute(template_inputs)
      hydrated_template_name: str = Template(template.template_name).substitute(template_inputs)
      hydrated_target: str = Template(template.target_location).substitute(template_inputs)
      template_path: Path = Path(os.path.join(Path.cwd(), hydrated_template_location, hydrated_template_name))
      target_path: Path   = Path(os.path.join(new_project_dir, hydrated_target, hydrated_template_name))
      populate_template(template_path, target_path, template_inputs)

  def _copy_wheel(self, project_options: ProjectTemplateOptions) -> None:
    """Note
    This is a temporary fix. The idea is to ultimately have the engine available 
    on pypi.org as a Python package. The created project would then automatically 
    install the package when the user runs the projects setup for doing unit testing.
    """
    engine_pkg = 'agents_playground-0.1.0-py3-none-any.whl'
    wheel_path: Path = Path(os.path.join(Path.cwd(), 'dist', engine_pkg))
    new_project_dir: Path = Path(os.path.join(project_options.project_parent_directory, project_options.project_name))
    destination_path: Path = Path(os.path.join(new_project_dir, 'libs', engine_pkg))
    shutil.copyfile(wheel_path, destination_path)