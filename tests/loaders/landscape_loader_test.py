import pytest

import os
from pathlib import Path

from jsonschema.exceptions import ValidationError

from agents_playground.loaders.landscape_loader import LandscapeLoaderException, LoadLandscapeIntoJSON, LoadSchemaIntoJSON, ValidateLandscapeFileExists, ValidateLandscapeJSON, ValidateSchemaExists

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

  def test_characteristics_is_required(self) -> None:
    context = {}
    context['landscape_json'] = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    LoadSchemaIntoJSON().process(context, schema_path, landscape_path='')

    with pytest.raises(ValidationError) as err:
      ValidateLandscapeJSON().process(context, schema_path, landscape_path='')
    assert "'characteristics' is a required property" in str(err.value)

  def test_tiles_is_required(self) -> None:
    context = {}
    context['landscape_json'] = {"characteristics": {}}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    LoadSchemaIntoJSON().process(context, schema_path, landscape_path='')

    with pytest.raises(ValidationError) as err:
      ValidateLandscapeJSON().process(context, schema_path, landscape_path='')
    assert "'tiles' is a required property" in str(err.value) 

  def test_valid_full_example(self) -> None:
    context = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)

    LoadSchemaIntoJSON().process(context, schema_path, landscape_path)
    LoadLandscapeIntoJSON().process(context, '', landscape_path = landscape_path)
    ValidateLandscapeJSON().process(context, schema_path, landscape_path)