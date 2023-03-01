from __future__ import annotations
import importlib

import sys
from types import ModuleType

from agents_playground.project.rules.directory_exists import DirectoryExists
from agents_playground.project.rules.init_file_exists import InitFileExist
from agents_playground.project.rules.scene_file_exists import SceneFileExist
from agents_playground.project.rules.valid_module_name import ValidModuleName

class ProjectLoader:
  """
  Responsible for loading a Simulation Project.
  """
  def __init__(self) -> None:
    self._validators = [
      ValidModuleName(),
      DirectoryExists(),
      InitFileExist(),
      SceneFileExist()
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
    Loads a project. If the project has already been loaded then it is reloaded.
    - module_name: The name of the project to load.
    - project_path: The path to where the project is located.

    Note: Reloading is handled by the project itself by defining a top level 
    reload() function.
    """
    if module_name in sys.modules:
      project_module: ModuleType = sys.modules[module_name]    
      project_module.reload()
    else:
      init_path: str = f'{project_path}/__init__.py'
      loader = importlib.machinery.SourceFileLoader(fullname=module_name, path=init_path)
      spec = importlib.util.spec_from_loader(loader.name, loader)
      if spec is not None:
        module  = importlib.util.module_from_spec(spec)
        if module is not None:
          sys.modules[module_name] = module
          spec_loader = spec.loader
          if spec_loader is not None:
            spec_loader.exec_module(module)
          else: 
            raise Exception(f'Unable to create a spec loader for module {module_name}.')
        else:
          raise Exception(f'Unable to load the {module_name} module.')
      else:
        raise Exception(f'Failed to build a spec from {init_path}.')