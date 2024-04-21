
from abc import abstractmethod
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
import os
import sys
from types import ModuleType
from typing import Protocol

from agents_playground.funcs import get_or_raise

SPEC_FAILED_ERROR_MSG          = 'Failed to build a spec from project path.'
MOD_FAILED_FROM_SPEC_ERROR_MSG = 'Unable to load the project\'s module.'
SPEC_LOADER_ERROR_MSG          = 'Unable to create a spec loader for the project\'s module.'

class ProjectValidator(Protocol):
  @abstractmethod
  def validate(self, module_name: str, module_path: str) -> bool:
    """
    Validates a project for a specific characteristic.
    """    

class ProjectLoaderError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class ValidModuleName(ProjectValidator):
  """
  Per Pep-8: https://peps.python.org/pep-0008/#package-and-module-names
  Modules should have short, all-lowercase names. 
  Underscores can be used in the module name if it improves readability.
  """
  def validate(self, module_name: str, module_path: str) -> bool:
    if not module_name.islower() or not module_name.isidentifier():
      raise ProjectLoaderError(f'The module name {module_name} is not formatted correctly. Modules must be all lowercase. Underscores are allowed.')
    return True
  
class DirectoryExists(ProjectValidator):
  def validate(self, module_name: str, module_path: str) -> bool:
    if not os.path.isdir(module_path):
      raise ProjectLoaderError(f'The module path {module_path} does not exist.')
    return True
  
class InitFileExist(ProjectValidator):
  def validate(self, module_name: str, module_path: str) -> bool:
    if not os.path.exists(os.path.join(module_path, '__init__.py')):
      raise ProjectLoaderError(f'The module does not contain an __init__.py file.')
    return True
  
class SceneFileExist(ProjectValidator):
  def validate(self, module_name: str, module_path: str) -> bool:
    if not os.path.exists(os.path.join(module_path, 'scene.json')):
      raise ProjectLoaderError(f'The module does not contain a scene.json file.')
    return True
  
class ProjectLoader:
  """
  Loads a simulation into memory.

  TODO: Rewrite the legacy ProjectLoader to be appropriate for the JSON based project structure.
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

  def load(self, module_name: str, project_path: str) -> None:
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