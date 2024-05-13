from typing import Any

from agents_playground.loaders import JSONFileLoader, search_directories
from agents_playground.scene import Scene

SCHEMA_PATH='agents_playground/scene/file/scene.schema.json'

class SceneLoader:
  def __init__(self):
    self._json_loader = JSONFileLoader()

  def load(self, scene_path: str) -> Scene:
    # 1. Load the scene
    loader_context = {}
    self._json_loader.load(
      context     = loader_context, 
      schema_path = SCHEMA_PATH, 
      file_path   = scene_path, 
      search_directories = search_directories()
    )
    json_obj: dict = loader_context['json_content']
    scene = Scene(**json_obj)
    return scene