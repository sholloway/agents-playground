import os
from pathlib import Path
from jsonschema import ValidationError
import pytest

from agents_playground.loaders import JSONFileLoader, LoadSchemaIntoMemory, ValidateJSONWithSchema, ValidateSchema

SCHEMA_PATH='agents_playground/scene/file/scene.schema.json'

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

  def test_landscape_ref_must_be_json(self) -> None:
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
      "landscape": "path/to/something/that/is/not/a/json/file/example.toml"
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
    pass