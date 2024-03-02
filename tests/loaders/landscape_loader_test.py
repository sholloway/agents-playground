import pytest

import os
from pathlib import Path

from jsonschema.exceptions import ValidationError

from agents_playground.loaders import JSONFileLoaderStepException, LoadJSONIntoMemory, LoadSchemaIntoMemory, ValidateJSONFileExists, ValidateJSONWithSchema, ValidateSchemaExists


class TestLandscapeLoader:
  """Tests validating landscape files using JSON Schema."""
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

  def test_landscape_exists(self) -> None: 
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    assert ValidateJSONFileExists().process(
      context = {},
      schema_path='',
      file_path = landscape_path
    ) == True
  
  def test_landscape_does_not_exist(self) -> None:
    bad_landscape_path = 'bad/path/to/landscape.json'
    with pytest.raises(JSONFileLoaderStepException) as err: 
      assert ValidateJSONFileExists().process(
        context = {},
        schema_path = '',
        file_path = bad_landscape_path
      ) == True
    assert str(err.value) == f'Could not find the JSON file at {bad_landscape_path}.'   

  def test_load_landscape_json(self) -> None:
    context = {}
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    LoadJSONIntoMemory().process(context, '', landscape_path = landscape_path)
    assert context.get('json_content') is not None 
  
  def test_load_schema_json(self) -> None:
    context = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)
    LoadSchemaIntoMemory().process(context, schema_path, landscape_path)
    assert context.get('schema_content') is not None 

  def test_characteristics_is_required(self) -> None:
    context = {}
    context['json_content'] = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    LoadSchemaIntoMemory().process(context, schema_path, landscape_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, schema_path, landscape_path='')
    assert "'characteristics' is a required property" in str(err.value)

  def test_tiles_is_required(self) -> None:
    context = {}
    context['json_content'] = {"characteristics": {}}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    LoadSchemaIntoMemory().process(context, schema_path, landscape_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, schema_path, landscape_path='')
    assert "'tiles' is a required property" in str(err.value) 

  def test_valid_full_example(self) -> None:
    context = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)

    LoadSchemaIntoMemory().process(context, schema_path, landscape_path)
    LoadJSONIntoMemory().process(context, '', landscape_path = landscape_path)
    ValidateJSONWithSchema().process(context, schema_path, landscape_path)