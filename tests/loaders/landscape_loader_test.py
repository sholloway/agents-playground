from typing import Any
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
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_file_characteristics import LandscapeFileCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile
from agents_playground.spatial.landscape.types import LandscapeGravityUOM, LandscapeMeshType
from agents_playground.uom import DateTime, LengthUOM, SystemOfMeasurement

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
    assert_landscape_characteristics(landscape.characteristics) 
    assert_physicality(landscape.physicality)
    assert_custom_attributes(landscape.custom_attributes)
    assert_tiles(landscape.tiles)

def assert_tiles(tiles: dict[Coordinate, Tile]):
  assert isinstance(tiles, dict)
  assert len(tiles) == 7
  assert tiles.get(Coordinate(0, 0, 0, 1)) is not None
  assert tiles.get(Coordinate(0, 0, 1, 6)) is not None
  assert tiles.get(Coordinate(0, 0, 2, 7)) is not None
  assert tiles.get(Coordinate(1, 0, 0, 8)) is not None
  assert tiles.get(Coordinate(-1, 0, 0, 9)) is not None
  assert tiles.get(Coordinate(0, 0, -1, 10)) is not None
  assert tiles.get(Coordinate(0, 0, -2, 11)) is not None
  
def assert_custom_attributes(ca: dict[str, Any]) -> None:
  assert isinstance(ca, dict)
  assert ca['ignore'] == 123

def assert_physicality(p: LandscapePhysicality) -> None:
  assert isinstance(p.gravity_uom, LandscapeGravityUOM)
  assert p.gravity_uom == LandscapeGravityUOM.METERS_PER_SECOND_SQUARED
  assert p.gravity_strength == 9.8
    
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

def assert_landscape_characteristics(lc: LandscapeCharacteristics) -> None:
  assert isinstance(lc.mesh_type, LandscapeMeshType)
  assert lc.mesh_type == LandscapeMeshType.SQUARE_TILE

  assert isinstance(lc.landscape_uom_system, SystemOfMeasurement)
  assert lc.landscape_uom_system == SystemOfMeasurement.METRIC

  assert isinstance(lc.tile_size_uom, LengthUOM)
  assert lc.tile_size_uom == LengthUOM.METER
  assert lc.tile_width == 1
  assert lc.tile_height == 1
  assert lc.tile_depth == 1