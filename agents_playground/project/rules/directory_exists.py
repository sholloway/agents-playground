import os
from agents_playground.project.project_loader_error import ProjectLoaderError
from agents_playground.project.rules.project_validator import ProjectValidator

class DirectoryExists(ProjectValidator):
  def validate(self, module_name: str, module_path: str) -> bool:
    if not os.path.isdir(module_path):
      raise ProjectLoaderError(f'The module path {module_path} does not exist.')
    return True