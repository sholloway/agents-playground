import pytest

import datetime as dt 
import os
from pathlib import Path

from jsonschema.exceptions import ValidationError
from agents_playground.fp import Maybe

from agents_playground.loaders import (
  JSONFileLoaderStepException, 
  LoadJSONIntoMemory, 
  LoadSchemaIntoMemory, 
  ValidateJSONFileExists, 
  ValidateJSONWithSchema, 
  ValidateSchemaExists
)
from agents_playground.loaders.landscape_loader import LandscapeLoader
from agents_playground.spatial.landscape.landscape_file_characteristics import LandscapeFileCharacteristics
from agents_playground.uom import DateTime

class TestLandscapeLoader:
  """Tests validating landscape files using JSON Schema."""
  def test_characteristics_is_required(self) -> None:
    context = {}
    context['json_content'] = {}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    LoadSchemaIntoMemory().process(context, schema_path, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, schema_path, file_path='')
    assert "'characteristics' is a required property" in str(err.value)

  def test_tiles_is_required(self) -> None:
    context = {}
    context['json_content'] = {"characteristics": {}}
    schema_path='agents_playground/spatial/landscape/file/landscape.schema.json'
    LoadSchemaIntoMemory().process(context, schema_path, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, schema_path, file_path='')
    assert "'tiles' is a required property" in str(err.value) 

  def test_valid_full_example(self) -> None:
    landscape_relative_path = 'agents_playground/spatial/landscape/file/landscape_example.json'
    landscape_path = os.path.join(Path.cwd(), landscape_relative_path)

    ll = LandscapeLoader()
    landscape = ll.load(landscape_path=landscape_path)
    assert_file_characteristics(landscape.file_characteristics)
    

def assert_file_characteristics(fc: Maybe[LandscapeFileCharacteristics]) -> None:
  assert fc.is_something()
  fc_unwrapped: LandscapeFileCharacteristics = fc.unwrap()
  assert fc_unwrapped.author.is_something() 
  assert fc_unwrapped.author.unwrap() == "John Smith"

  assert fc_unwrapped.license.is_something() 
  assert fc_unwrapped.license.unwrap() == "MIT"

  assert fc_unwrapped.contact.is_something()
  assert fc_unwrapped.contact.unwrap() == "john.smith@smiths.com"

  assert fc_unwrapped.creation_time.is_something()
  assert isinstance(fc_unwrapped.creation_time.unwrap(), DateTime)
  assert fc_unwrapped.creation_time.unwrap().tzinfo == dt.timezone.utc
  assert fc_unwrapped.creation_time.unwrap().year == 2024
  assert fc_unwrapped.creation_time.unwrap().month == 3
  assert fc_unwrapped.creation_time.unwrap().day == 1
  assert fc_unwrapped.creation_time.unwrap().hour == 12
  assert fc_unwrapped.creation_time.unwrap().minute == 42
  assert fc_unwrapped.creation_time.unwrap().second == 54
  assert fc_unwrapped.creation_time.unwrap().microsecond == 510655

  assert fc_unwrapped.updated_time.is_something()
  assert isinstance(fc_unwrapped.updated_time.unwrap(), DateTime)
  assert fc_unwrapped.updated_time.unwrap().tzinfo == dt.timezone.utc
  assert fc_unwrapped.updated_time.unwrap().year == 2024
  assert fc_unwrapped.updated_time.unwrap().month == 3
  assert fc_unwrapped.updated_time.unwrap().day == 4
  assert fc_unwrapped.updated_time.unwrap().hour == 14
  assert fc_unwrapped.updated_time.unwrap().minute == 9
  assert fc_unwrapped.updated_time.unwrap().second == 22
  assert fc_unwrapped.updated_time.unwrap().microsecond == 110655