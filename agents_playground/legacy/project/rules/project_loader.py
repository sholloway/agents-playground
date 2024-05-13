from __future__ import annotations

from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec

import sys
from types import ModuleType
from typing import Any
from agents_playground.funcs import get_or_raise

from agents_playground.legacy.project.rules.directory_exists import DirectoryExists
from agents_playground.legacy.project.rules.init_file_exists import InitFileExist
from agents_playground.legacy.project.rules.scene_file_exists import SceneFileExist
from agents_playground.legacy.project.rules.valid_module_name import ValidModuleName
  
SPEC_FAILED_ERROR_MSG          = 'Failed to build a spec from project path.'
MOD_FAILED_FROM_SPEC_ERROR_MSG = 'Unable to load the project\'s module.'
SPEC_LOADER_ERROR_MSG          = 'Unable to create a spec loader for the project\'s module.'
  
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

  def validate(self, module_name: str, project_path: str) -> bool:
    """
    Validates that a project is setup correctly. 
    Throws a ProjectLoaderError exception if any of rules are violated.

    Args:
    - module_name: The name of the project to validate.
    - project_path: The path to where the project is located.
    """
    return all([r.validate(module_name, project_path) for r in self._validators])
      
  def load_or_reload(self, module_name: str, project_path: str) -> None:
    """
    Loads a project. If the project has already been loaded then it is reloaded.
    - module_name: The name of the project to load.
    - project_path: The path to where the project is located.

    Note: Reloading is handled by the project itself by defining a top level 
    reload() function.
    """
    if module_name in sys.modules:
      self._reload_project(module_name)
    else:
      self._load_project(module_name, project_path)

  def _reload_project(self, module_name) -> None:
    project_module: ModuleType = sys.modules[module_name]    
    project_module.reload()

  def _load_project(self, module_name: str, project_path: str) -> None:
    init_path: str = f'{project_path}/__init__.py'
    loader = SourceFileLoader(fullname = module_name, path = init_path)
    spec = get_or_raise(spec_from_loader(loader.name, loader), Exception(SPEC_FAILED_ERROR_MSG))
    module = get_or_raise(module_from_spec(spec), Exception(MOD_FAILED_FROM_SPEC_ERROR_MSG))
    sys.modules[module_name] = module
    spec_loader = get_or_raise(spec.loader, Exception())
    spec_loader.exec_module(module)