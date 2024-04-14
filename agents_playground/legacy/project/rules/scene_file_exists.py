import os
from agents_playground.legacy.project.project_loader_error import ProjectLoaderError
from agents_playground.legacy.project.rules.project_validator import ProjectValidator

class SceneFileExist(ProjectValidator):
  def validate(self, module_name: str, module_path: str) -> bool:
    if not os.path.exists(os.path.join(module_path, 'scene.toml')):
      raise ProjectLoaderError(f'The module does not contain a scene.toml file.')
    return True