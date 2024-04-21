# Note: All of the template data can use $var and ${var} for dynamic population.
import importlib.metadata
import os
from pathlib import Path
import shutil
from string import Template
from typing import Any
from agents_playground.projects.simulation_template_options import SimulationTemplateOptions
from agents_playground.projects.template_file import TemplateFile

TEMPLATES = [
  TemplateFile('__init__.py',         '$default_template_path', '$project_pkg'),
  TemplateFile('cube_agent_def.json', '$default_template_path', '$project_pkg'),
  TemplateFile('cube.obj',            '$default_template_path', '$project_pkg'),
  TemplateFile('landscape.json',      '$default_template_path', '$project_pkg'),
  TemplateFile('scene_test.py',       '$default_template_path', 'tests'),
  TemplateFile('scene.json',          '$default_template_path', '$project_pkg'),
  TemplateFile('scene.py',            '$default_template_path', '$project_pkg')
]

def populate_template(
  path_to_template: Path, 
  path_to_target: Path, 
  template_inputs: dict[str, Any]
) -> None:
  scene_template: str = path_to_template.read_text()
  scene_file = Template(scene_template).substitute(template_inputs)
  path_to_target.write_text(scene_file)
  
class NewSimulationBuilderException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class NewSimulationBuilder:
  """
  Creates a new simulation project. Copies the template files to the target 
  directory and populates them based on the options provided.
  """
  def build(self, simulation_options: SimulationTemplateOptions) -> None:
    """Assumes all validation has already happened and attempts to create a new simulation project."""
    self._prevent_over_writing_existing_directories(simulation_options)
    self._copy_template_directory(simulation_options)
    self._rename_pkg_directory(simulation_options)
    self._generate_project_files(simulation_options)
    self._copy_wheel(simulation_options)

  def _prevent_over_writing_existing_directories(self, simulation_options: SimulationTemplateOptions) -> None:
    new_sim_dir = os.path.join(simulation_options.parent_directory, simulation_options.simulation_name)
    if os.path.isdir(new_sim_dir):
      error_msg = f'Cannot create the new simulation.\nThe directory {new_sim_dir} already exists.\nPlease specify a different project name.'
      raise NewSimulationBuilderException(error_msg)
    
  def _copy_template_directory(self, simulation_options: SimulationTemplateOptions) -> None:
    try:
      new_sim_dir = os.path.join(simulation_options.parent_directory, simulation_options.simulation_name)
      template_dir = os.path.join(Path.cwd(), 'agents_playground/templates/new_sim')
      shutil.copytree(template_dir, new_sim_dir)
    except Exception as e:
      raise NewSimulationBuilderException('Failed to copy the template directory for the new simulation.') from e 

  def _rename_pkg_directory(self, simulation_options: SimulationTemplateOptions) -> None:
    try: 
      package_dir = os.path.join(simulation_options.parent_directory, simulation_options.simulation_name, 'project_pkg')
      project_pkg_dir = os.path.join(simulation_options.parent_directory, simulation_options.simulation_name, simulation_options.simulation_name)
      Path(package_dir).rename(project_pkg_dir)
    except Exception as e:
      raise NewSimulationBuilderException('Failed to rename the package directory for the new simulation.') from e

  def _generate_project_files(self, simulation_options: SimulationTemplateOptions) -> None:
    try: 
      template_inputs = simulation_options._asdict()
      template_inputs['project_pkg'] = simulation_options.simulation_name
      template_inputs['default_template_path'] = 'agents_playground/templates/base_sim_files'
      new_project_dir = os.path.join(simulation_options.parent_directory, simulation_options.simulation_name)

      for template in TEMPLATES:
        hydrated_template_location: str = Template(template.template_location).substitute(template_inputs)
        hydrated_template_name: str = Template(template.template_name).substitute(template_inputs)
        hydrated_target: str = Template(template.target_location).substitute(template_inputs)
        template_path: Path = Path(os.path.join(Path.cwd(), hydrated_template_location, hydrated_template_name))
        target_path: Path   = Path(os.path.join(new_project_dir, hydrated_target, hydrated_template_name))
        populate_template(template_path, target_path, template_inputs)
    except Exception as e:
      raise NewSimulationBuilderException('Failed to generate the project files for the new simulation.') from e

  def _copy_wheel(self, simulation_options: SimulationTemplateOptions) -> None:
    """Note
    This is a temporary fix. The intent is to ultimately have the engine available 
    on pypi.org as a Python package. The created project would then automatically 
    install the package when the user runs the projects setup for doing unit testing.
    """
    try:
      # Note: There is a thread around dealing with package versions for 
      # poetry based packages.
      # https://github.com/python-poetry/poetry/issues/273 
      pkg_version = importlib.metadata.version('agents_playground')
      engine_pkg = f'agents_playground-{pkg_version}-py3-none-any.whl'
      wheel_path: Path = Path(os.path.join(Path.cwd(), 'dist', engine_pkg))
      new_project_dir: Path = Path(os.path.join(simulation_options.parent_directory, simulation_options.simulation_name))
      destination_path: Path = Path(os.path.join(new_project_dir, 'libs', engine_pkg))
      shutil.copyfile(wheel_path, destination_path)
    except Exception as e:
      raise NewSimulationBuilderException("Failed to copy the engine's wheel while trying to set up the new simulation.") from e