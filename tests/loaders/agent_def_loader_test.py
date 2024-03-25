import os
from pathlib import Path
from jsonschema import ValidationError
import pytest

from agents_playground.loaders import JSONFileLoader, LoadSchemaIntoMemory, ValidateJSONWithSchema, ValidateSchema
from agents_playground.loaders.agent_definition_loader import AGENT_DEF_SCHEMA_PATH

class TestAgentDefLoader:
  def test_valid_schema(self) -> None:
    context = {}
    LoadSchemaIntoMemory().process(context, AGENT_DEF_SCHEMA_PATH, '')
    ValidateSchema().process(context, AGENT_DEF_SCHEMA_PATH, '')

  def test_model_is_required(self) -> None:
    context = {}
    context['json_content'] = {}
    LoadSchemaIntoMemory().process(context, AGENT_DEF_SCHEMA_PATH, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, AGENT_DEF_SCHEMA_PATH, file_path='')
    assert "'agent_model' is a required property" in str(err.value)
  
  def test_model_transformation_is_required(self) -> None:
    context = {}
    context['json_content'] = { 'agent_model': 'blah'}
    LoadSchemaIntoMemory().process(context, AGENT_DEF_SCHEMA_PATH, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, AGENT_DEF_SCHEMA_PATH, file_path='')
    assert "'model_transformation' is a required property" in str(err.value)

  def test_view_frustum_is_required(self) -> None:
    context = {}
    context['json_content'] = { 
      'agent_model': False,
      'model_transformation': False
    }

    LoadSchemaIntoMemory().process(context, AGENT_DEF_SCHEMA_PATH, file_path='')

    with pytest.raises(ValidationError) as err:
      ValidateJSONWithSchema().process(context, AGENT_DEF_SCHEMA_PATH, file_path='')
    assert "'view_frustum' is a required property" in str(err.value)

  def test_json_valid_full_example(self) -> None:
    scene_rel_path = "agents_playground/agents/file/agent_def.example.json"
    agent_def_path = os.path.join(Path.cwd(), scene_rel_path)
    context = {}
    jfl = JSONFileLoader()
    assert jfl.load(context, AGENT_DEF_SCHEMA_PATH, agent_def_path)
    assert context['json_content'] is not None 
