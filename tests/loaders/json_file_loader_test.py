import os
from pathlib import Path
import pytest

from agents_playground.loaders import (
  JSONFileLoader,
  JSONFileLoaderStepException,
  LoadJSONIntoMemory,
  LoadSchemaIntoMemory,
  ValidateJSONFileExists,
  ValidateJSONWithSchema, 
  ValidateSchemaExists
)

class TestValidateSchemaExists:
  def test_schema_exists(self) -> None:
    assert ValidateSchemaExists().process(
      context = {},
      schema_path='agents_playground/spatial/landscape/file/landscape.schema.json',
      file_path = ''
    ) == True

  def test_schema_does_not_exist(self) -> None:
    bad_schema_path = 'bad/path/to/landscape.schema.json'
    with pytest.raises(JSONFileLoaderStepException) as err: 
      assert ValidateSchemaExists().process(
        context = {},
        schema_path = bad_schema_path,
        file_path = ''
      ) == True
    assert str(err.value) == f'Could not find the schema {bad_schema_path}.'  

class TestValidateJSONFileExists:
  def test_json_file_exists(self) -> None: 
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    assert ValidateJSONFileExists().process(
      context = {},
      schema_path='',
      file_path = landscape_path
    ) == True
  
  def test_json_file_does_not_exist(self) -> None:
    bad_landscape_path = 'bad/path/to/landscape.json'
    with pytest.raises(JSONFileLoaderStepException) as err: 
      assert ValidateJSONFileExists().process(
        context = {},
        schema_path = '',
        file_path = bad_landscape_path
      ) == True
    assert str(err.value) == f'Could not find the JSON file at {bad_landscape_path}.'

class TestLoadJSONIntoMemory:
  def test_load_landscape_json(self) -> None:
    context = {}
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    LoadJSONIntoMemory().process(context, '', file_path = landscape_path)
    assert context.get('json_content') is not None 

class TestLoadSchemaIntoMemory:
  def test_load_schema_json(self) -> None:
    context = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    LoadSchemaIntoMemory().process(context, schema_path, landscape_path)
    assert context.get('schema_content') is not None 

class TestValidateJSONWithSchema:
  def test_valid_full_example(self) -> None:
    context = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)

    LoadSchemaIntoMemory().process(context, schema_path, landscape_path)
    LoadJSONIntoMemory().process(context, '', file_path = landscape_path)
    ValidateJSONWithSchema().process(context, schema_path, landscape_path)

class TestJSONFileLoader:
  """Tests loading and validating a JSON file with a JSON Schema file."""
  def test_valid_full_example(self) -> None:
    jfl = JSONFileLoader()
    context = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    assert jfl.load(context, schema_path, landscape_path)
    assert context['json_content'] is not None 
