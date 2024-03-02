from abc import ABC, abstractmethod
import os
from pathlib import Path
from typing import Any

import jsonschema as js

class LandscapeLoader:
  def __init__(self):
    self._steps = [
      # ValidateSchemaExists(),
      # ValidateSceneFileExists(),
      # LoadSchemaIntoJSON(),
      # LoadLandscapeIntoJSON(),
      # ValidateLandscapeJSON()
    ]

  def load(self, context: dict[str, Any], schema_path: str, landscape_path: str) -> bool:
    return all([ r.process(context, schema_path, landscape_path) for r in self._steps])
