from abc import ABC, abstractmethod
from typing import Any
import pytest

import os
from pathlib import Path

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

class TestLandscapeLoader:
  """Tests validating landscape files using JSON Schema."""
  def test_schema_exists(self) -> None:
    assert ValidateSchemaExists().process(
      context = {},
      schema_path='agents_playground/spatial/landscape/file/landscape.schema.json',
      landscape_path = ''
    ) == True

  def test_schema_does_not_exist(self) -> None:
    bad_schema_path = 'bad/path/to/landscape.schema.json'
    with pytest.raises(LandscapeLoaderException) as err: 
      assert ValidateSchemaExists().process(
        context = {},
        schema_path = bad_schema_path,
        landscape_path = ''
      ) == True
    assert str(err.value) == f'Could not find the schema {bad_schema_path}.'   

  def test_landscape_exists(self) -> None: 
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    assert ValidateLandscapeFileExists().process(
      context = {},
      schema_path='',
      landscape_path = landscape_path
    ) == True
  
  def test_landscape_does_not_exist(self) -> None:
    bad_landscape_path = 'bad/path/to/landscape.json'
    with pytest.raises(LandscapeLoaderException) as err: 
      assert ValidateLandscapeFileExists().process(
        context = {},
        schema_path = '',
        landscape_path = bad_landscape_path
      ) == True
    assert str(err.value) == f'Could not find the landscape file at {bad_landscape_path}.'   

  def test_load_landscape_json(self) -> None:
    context = {}
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    LoadLandscapeIntoJSON().process(context, '', landscape_path = landscape_path)
    assert context.get('landscape_json') is not None 
  
  def test_load_schema_json(self) -> None:
    context = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    LoadSchemaIntoJSON().process(context, schema_path, landscape_path)
    assert context.get('schema_json') is not None 

  def test_schema_validation(self) -> None:
    context = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)

    LoadSchemaIntoJSON().process(context, schema_path, landscape_path)
    LoadLandscapeIntoJSON().process(context, '', landscape_path = landscape_path)
    LoadLandscapeIntoJSON().process(context, schema_path, landscape_path)