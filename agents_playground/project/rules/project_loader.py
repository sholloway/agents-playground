from __future__ import annotations
import importlib
from importlib.machinery import ModuleSpec
import pkgutil

import sys
from types import ModuleType

from agents_playground.project.rules.directory_exists import DirectoryExists
from agents_playground.project.rules.entities_directory_exists import EntitiesDirectoryExists
from agents_playground.project.rules.init_file_exists import InitFileExist
from agents_playground.project.rules.renderer_directory_exists import RendererDirectoryExists
from agents_playground.project.rules.scene_file_exists import SceneFileExist
from agents_playground.project.rules.tasks_directory_exists import TasksDirectoryExists
from agents_playground.project.rules.valid_module_name import ValidModuleName

class ProjectLoader:
  """
  Responsible for loading a Simulation Project.
  """
  def __init__(self) -> None:
    self._validators = [
      ValidModuleName(),
      DirectoryExists(),
      # InitFileExist(),
      SceneFileExist(),
      RendererDirectoryExists(),
      EntitiesDirectoryExists(),
      TasksDirectoryExists(),
    ]

  def validate(self, module_name: str, project_path: str) -> None:
    """
    Validates that a project is setup correctly. 
    Throws a ProjectLoaderError exception if any of rules are violated.

    Args:
    - module_name: The name of the project to validate.
    - project_path: The path to where the project is located.
    """
    [rule.validate(module_name, project_path) for rule in self._validators]

  def load(self, module_name: str, project_path: str) -> None:
    """
    Loads a project.
    - module_name: The name of the project to load.
    - project_path: The path to where the project is located.
    """

    if module_name in sys.modules:
      print('doing nothing')
      project_module: ModuleType = sys.modules[module_name]    

      # Rather than try to reload the top module, I think I need to walk the package
      # And reload the entire thing.
      # importlib.reload(project_module)
      # print(f'reloaded {module_name}')

      # pkgutil.walk_packages()

    else:
      # spec = importlib.util.spec_from_file_location(module_name, f'{project_path}/{module_name}.py')

      loader = importlib.machinery.SourceFileLoader(fullname=module_name, path=f'{project_path}/__init__.py')
      spec = importlib.util.spec_from_loader(loader.name, loader)
      module  = importlib.util.module_from_spec(spec)
      sys.modules[module_name] = module
      spec.loader.exec_module(module)
      print(f'loaded {module_name}')

    # module.MySim()

