from abc import ABC, abstractmethod
import os
from pathlib import Path
from typing import Any

import jsonschema as js

class LandscapeLoader:
  def __init__(self):
    self._steps = [
      ValidateSchemaExists(),
      ValidateLandscapeFileExists(),
      LoadSchemaIntoJSON(),
      LoadLandscapeIntoJSON(),
      ValidateLandscapeJSON()
    ]

  def load(self, context: dict[str, Any], schema_path: str, landscape_path: str) -> bool:
    return all([ r.validate(context, schema_path, schema_path) for r in self._steps])
      

class LandscapeLoaderException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class LandscapeProcessor(ABC):
    @abstractmethod
    def process(self, context: dict[str, Any], schema_path: str, landscape_path: str) -> bool:
      """
      Runs a step in loading a Landscape.
      """    

class ValidateSchemaExists(LandscapeProcessor):
  def process(self, context: dict[str, Any], schema_path: str, landscape_path: str) -> bool: 
    if not os.path.exists(os.path.join(Path.cwd(), schema_path)):
      raise LandscapeLoaderException(f'Could not find the schema {schema_path}.')
    return True

class ValidateLandscapeFileExists(LandscapeProcessor):
  def process(self, context: dict[str, Any], schema_path: str, landscape_path: str) -> bool: 
    if not os.path.exists(landscape_path):
      raise LandscapeLoaderException(f'Could not find the landscape file at {landscape_path}.')
    return True
  
import json
class LoadLandscapeIntoJSON(LandscapeProcessor):
  def process(self, context: dict[str, Any], schema_path: str, landscape_path: str) -> bool: 
    with open(file = landscape_path, mode = 'r', encoding="utf-8") as filereader:
      context['landscape_json'] = json.load(filereader)
    return True
  
class LoadSchemaIntoJSON(LandscapeProcessor):
  def process(self, context: dict[str, Any], schema_path: str, landscape_path: str) -> bool: 
    with open(file = schema_path, mode = 'r', encoding="utf-8") as filereader:
      context['schema_json'] = json.load(filereader)
    return True
  
class ValidateLandscapeJSON(LandscapeProcessor):
  def process(self, context: dict[str, Any], schema_path: str, landscape_path: str) -> bool: 
    js.validate(
      instance = context['landscape_json'],
      schema = context['schema_json']
    )
    return True