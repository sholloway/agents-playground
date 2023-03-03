import os
from agents_playground.project.project_loader_error import ProjectLoaderError
from agents_playground.project.rules.project_validator import ProjectValidator

class InitFileExist(ProjectValidator):
  def validate(self, module_name: str, module_path: str) -> bool:
    if not os.path.exists(os.path.join(module_path, '__init__.py')):
      raise ProjectLoaderError(f'The module does not contain an __init__.py file.')
    return True