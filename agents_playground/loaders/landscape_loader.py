from typing import Any

from agents_playground.loaders import (
  LoadJSONIntoMemory, 
  LoadSchemaIntoMemory, 
  ValidateJSONFileExists, 
  ValidateJSONWithSchema, 
  ValidateSchemaExists
)

class LandscapeLoader:
  def __init__(self):
    self._steps = [
      ValidateSchemaExists(),
      ValidateJSONFileExists(),
      LoadSchemaIntoMemory(),
      LoadJSONIntoMemory(),
      ValidateJSONWithSchema()
    ]

  def load(self, context: dict[str, Any], schema_path: str, landscape_path: str) -> bool:
    return all([ r.process(context, schema_path, landscape_path) for r in self._steps])