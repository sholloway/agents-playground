from typing import Any

from agents_playground.loaders import JSONFileLoader
from agents_playground.spatial.landscape import Landscape

LANDSCAPE_SCHEMA_PATH = 'agents_playground/spatial/landscape/file/landscape.schema.json'

class LandscapeLoader:
  def __init__(self):
    self._json_loader = JSONFileLoader()

  def load(self, landscape_path: str) -> Landscape:
    loader_context = {}
    self._json_loader.load(
      context     = loader_context, 
      schema_path = LANDSCAPE_SCHEMA_PATH, 
      file_path   = landscape_path
    )
    json_obj: dict = loader_context['json_content']
    return Landscape(**json_obj)
