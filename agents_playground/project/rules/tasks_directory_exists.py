import os
from agents_playground.project.project_loader_error import ProjectLoaderError
from agents_playground.project.rules.project_validator import ProjectValidator

class TasksDirectoryExists(ProjectValidator):
  def validate(self, module_name: str, module_path: str) -> bool:
    if not os.path.isdir(os.path.join(module_path, 'tasks')):
      raise ProjectLoaderError(f'The module does not contain a tasks directory.')
    return True