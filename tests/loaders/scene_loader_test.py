import pytest

import datetime as dt 
import os
from pathlib import Path
from jsonschema import ValidationError
from agents_playground.cameras.camera import Camera, Camera3d

from agents_playground.fp import Maybe
from agents_playground.loaders import JSONFileLoader, LoadSchemaIntoMemory, ValidateJSONWithSchema, ValidateSchema
from agents_playground.loaders.scene_loader import SCHEMA_PATH, SceneLoader
from agents_playground.scene import Transformation
from agents_playground.scene.scene_characteristics import SceneCharacteristics
from agents_playground.scene.scene_file_characteristics import SceneFileCharacteristics
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.vector.vector3d import Vector3d
from agents_playground.uom import DateTime, LengthUOM, SystemOfMeasurement

class TestSceneLoader:
  def test_valid_schema(self) -> None:
    context = {}
    LoadSchemaIntoMemory().process(context, SCHEMA_PATH, '')
    ValidateSchema().process(context, SCHEMA_PATH, '')

  def test_characteristics_is_required(self) -> None:
    context = {}
    context['json_content'] = {}
    LoadSchemaIntoMemory().process(context, SCHEMA_PATH, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, SCHEMA_PATH, file_path='')
    assert "'characteristics' is a required property" in str(err.value)
  
  def test_camera_is_required(self) -> None:
    context = {}
    context['json_content'] = {
      "characteristics":{
        "scene_uom_system":"US_CUSTOMARY",
        "scene_distance_uom":"FEET"
      }
    }
    LoadSchemaIntoMemory().process(context, SCHEMA_PATH, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, SCHEMA_PATH, file_path='')
    assert "'camera' is a required property" in str(err.value)
  
  def test_landscape_is_required(self) -> None:
    context = {}
    context['json_content'] = {
      "characteristics":{
        "scene_uom_system":"US_CUSTOMARY",
        "scene_distance_uom":"FEET"
      },
      "camera":{
        "position": [1,2,3],
        "target": [0,0,0],
        "vertical_field_of_view": 72,
        "near_plane": 0.1,
        "far_plane": 100
      }
    }
    LoadSchemaIntoMemory().process(context, SCHEMA_PATH, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, SCHEMA_PATH, file_path='')
    assert "'landscape' is a required property" in str(err.value)

  def test_landscape_transformation_is_required(self) -> None:
    context = {}
    context['json_content'] = {
      "characteristics":{
        "scene_uom_system":"US_CUSTOMARY",
        "scene_distance_uom":"FEET"
      },
      "camera":{
        "position": [1,2,3],
        "target": [0,0,0],
        "vertical_field_of_view": 72,
        "near_plane": 0.1,
        "far_plane": 100
      },
      "landscape": "path/to/something/that/is/not/a/json/file/example.toml",
    }
    LoadSchemaIntoMemory().process(context, SCHEMA_PATH, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, SCHEMA_PATH, file_path='')
    assert "'landscape_transformation' is a required property" in str(err.value)
  
  def test_landscape_ref_must_be_json(self) -> None:
    context = {}
    context['json_content'] = {
      "characteristics":{
        "name": "my_sim",
        "title": "My Sim",
        "description": "A sim.",
        "scene_uom_system":"US_CUSTOMARY",
        "scene_distance_uom":"FEET"
      },
      "camera":{
        "position": [1,2,3],
        "target": [0,0,0],
        "vertical_field_of_view": 72,
        "near_plane": 0.1,
        "far_plane": 100
      },
      "landscape": "path/to/something/that/is/not/a/json/file/example.toml",
      "landscape_transformation":{
        "translation": [0,0,0],
        "rotation": [0,0,0],
        "scale": [0,0,0]
      },
      "landscape_location": [0,0,0],
      "landscape_scale": [0,0,0],
      "landscape_rotation": [0,0,0]
    }
    LoadSchemaIntoMemory().process(context, SCHEMA_PATH, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, SCHEMA_PATH, file_path='')
    assert "does not match '.json$'" in str(err.value)

  def test_json_valid_full_example(self) -> None:
    scene_rel_path = "agents_playground/scene/file/scene_example.json"
    scene_path = os.path.join(Path.cwd(), scene_rel_path)
    context = {}
    jfl = JSONFileLoader()
    assert jfl.load(context, SCHEMA_PATH, scene_path)
    assert context['json_content'] is not None 

  def test_load_scene(self) -> None:
    # Use the SceneLoader in this test.
    scene_rel_path = "agents_playground/scene/file/scene_example.json"
    scene_path = os.path.join(Path.cwd(), scene_rel_path)
    sl = SceneLoader()
    scene = sl.load(scene_path)
    assert scene is not None
    assert_file_characteristics(scene.file_characteristics)
    assert_scene_characteristics(scene.characteristics) 
    assert_scene_camera(scene.camera)
    assert isinstance(scene.landscape, Landscape)
    assert isinstance(scene.landscape_transformation, Transformation)

def assert_scene_camera(c: Camera) -> None:
  assert isinstance(c, Camera3d)
  assert c.position == Vector3d(1, 2, 3)
  assert c.target == Vector3d(0, 0, 0)

def assert_scene_characteristics(c: SceneCharacteristics) -> None:
  assert isinstance(c, SceneCharacteristics)
  assert isinstance(c.scene_uom_system,SystemOfMeasurement)
  assert isinstance(c.scene_distance_uom,LengthUOM)

def assert_file_characteristics(fc: Maybe[SceneFileCharacteristics]) -> None:
  assert fc.is_something()
  fc_unwrapped: SceneFileCharacteristics = fc.unwrap()
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