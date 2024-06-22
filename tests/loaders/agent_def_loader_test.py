import os
from pathlib import Path
from jsonschema import ValidationError
import pytest

from agents_playground.agents.default.fuzzy_agent_action_selector import (
    FuzzyAgentActionSelector,
)
from agents_playground.fp import Something
from agents_playground.loaders import (
    JSONFileLoader,
    LoadSchemaIntoMemory,
    ValidateJSONWithSchema,
    ValidateSchema,
    search_directories,
)
from agents_playground.loaders.agent_definition_loader import (
    AGENT_DEF_SCHEMA_PATH,
    AgentDefinition,
    AgentDefinitionLoader,
    FsmAgentStateModel,
    ModelTransformation,
)
from agents_playground.spatial.frustum import Frustum3d
from agents_playground.spatial.vector.vector3d import Vector3d

search_dirs = search_directories()


class TestAgentDefinitionSchema:
    def test_valid_schema(self) -> None:
        context = {}
        LoadSchemaIntoMemory().process(context, AGENT_DEF_SCHEMA_PATH, "", search_dirs)
        ValidateSchema().process(context, AGENT_DEF_SCHEMA_PATH, "", search_dirs)

    def test_model_is_required(self) -> None:
        context = {}
        context["json_content"] = {}
        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context,
                AGENT_DEF_SCHEMA_PATH,
                file_path="",
                search_directories=search_dirs,
            )
        assert "'agent_model' is a required property" in str(err.value)

    def test_model_transformation_is_required(self) -> None:
        context = {}
        context["json_content"] = {"agent_model": "blah"}
        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context,
                AGENT_DEF_SCHEMA_PATH,
                file_path="",
                search_directories=search_dirs,
            )
        assert "'model_transformation' is a required property" in str(err.value)

    def test_view_frustum_is_required(self) -> None:
        context = {}
        context["json_content"] = {"agent_model": False, "model_transformation": False}

        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context,
                AGENT_DEF_SCHEMA_PATH,
                file_path="",
                search_directories=search_dirs,
            )
        assert "'view_frustum' is a required property" in str(err.value)

    def test_agent_state_model_requires_agent_states(self) -> None:
        context = {}
        context["json_content"] = {
            "agent_model": "path/to/a/model.obj",
            "model_transformation": {
                "translation": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
            "view_frustum": {
                "near_plane": 0.1,
                "far_plane": 100,
                "vertical_field_of_view": 45,
            },
            "agent_state_model": {},
        }

        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context,
                AGENT_DEF_SCHEMA_PATH,
                file_path="",
                search_directories=search_dirs,
            )
        assert "'agent_states' is a required property" in str(err.value)

    def test_agent_state_model_requires_initial_agent_state(self) -> None:
        context = {}
        context["json_content"] = {
            "agent_model": "path/to/a/model.obj",
            "model_transformation": {
                "translation": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
            "view_frustum": {
                "near_plane": 0.1,
                "far_plane": 100,
                "vertical_field_of_view": 45,
            },
            "agent_state_model": {"agent_states": []},
        }

        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context,
                AGENT_DEF_SCHEMA_PATH,
                file_path="",
                search_directories=search_dirs,
            )
        assert "'initial_agent_state' is a required property" in str(err.value)

    def test_agent_state_model_state_transition_map_is_required(self) -> None:
        context = {}
        context["json_content"] = {
            "agent_model": "path/to/a/model.obj",
            "model_transformation": {
                "translation": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
            "view_frustum": {
                "near_plane": 0.1,
                "far_plane": 100,
                "vertical_field_of_view": 45,
            },
            "agent_state_model": {"agent_states": [], "initial_agent_state": ""},
        }

        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context,
                AGENT_DEF_SCHEMA_PATH,
                file_path="",
                search_directories=search_dirs,
            )
        assert "'state_transition_map' is a required property" in str(err.value)

    def test_agent_states_cannot_be_empty(self) -> None:
        context = {}
        context["json_content"] = {
            "agent_model": "path/to/a/model.obj",
            "model_transformation": {
                "translation": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
            "view_frustum": {
                "near_plane": 0.1,
                "far_plane": 100,
                "vertical_field_of_view": 45,
            },
            "agent_state_model": {
                "agent_states": [],
                "initial_agent_state": "fake",
                "state_transition_map": ["fake"],
            },
        }

        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context,
                AGENT_DEF_SCHEMA_PATH,
                file_path="",
                search_directories=search_dirs,
            )
        # "[] should be non-empty\n\nFailed validating 'minItems' in schema['properties']['agent_state_model']['properties']['st...n     'type': 'array',\n     'uniqueItems': True}\n\nOn instance['agent_state_model']['state_transition_map']:\n    []"
        assert "agent_states" in str(err.value)
        assert "[] should be non-empty" in str(err.value)

    def test_agent_state_transition_map_cannot_be_empty(self) -> None:
        context = {}
        context["json_content"] = {
            "agent_model": "path/to/a/model.obj",
            "model_transformation": {
                "translation": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
            "view_frustum": {
                "near_plane": 0.1,
                "far_plane": 100,
                "vertical_field_of_view": 45,
            },
            "agent_state_model": {
                "agent_states": ["A"],
                "initial_agent_state": "",
                "state_transition_map": [],
            },
        }

        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context,
                AGENT_DEF_SCHEMA_PATH,
                file_path="",
                search_directories=search_dirs,
            )
        assert "state_transition_map" in str(err.value)
        assert "[] should be non-empty" in str(err.value)

    def test_state_transition_with_functions(self) -> None:
        context = {}
        context["json_content"] = {
            "agent_model": "path/to/a/model.obj",
            "model_transformation": {
                "translation": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
            "view_frustum": {
                "near_plane": 0.1,
                "far_plane": 100,
                "vertical_field_of_view": 45,
            },
            "agent_state_model": {
                "agent_states": ["A", "B", "C"],
                "initial_agent_state": "A",
                "state_transition_map": [
                    {
                        "current_state": "A",
                        "transitions_to": ["B"],
                        "transitions_when": "full_moon",
                    },
                ],
            },
        }

        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )
        ValidateJSONWithSchema().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

    def test_state_transition_with_likelihood(self) -> None:
        context = {}
        context["json_content"] = {
            "agent_model": "path/to/a/model.obj",
            "model_transformation": {
                "translation": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
            "view_frustum": {
                "near_plane": 0.1,
                "far_plane": 100,
                "vertical_field_of_view": 45,
            },
            "agent_state_model": {
                "agent_states": ["A", "B", "C"],
                "initial_agent_state": "A",
                "state_transition_map": [
                    {"current_state": "A", "transitions_to": ["B"], "likelihood": 0.75},
                    {"current_state": "B", "transitions_to": ["C"], "likelihood": 0.1},
                    {"current_state": "C", "transitions_to": ["A"], "likelihood": 1},
                ],
            },
        }

        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )
        ValidateJSONWithSchema().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

    def test_state_transition_with_next_state_weights(self) -> None:
        context = {}
        context["json_content"] = {
            "agent_model": "path/to/a/model.obj",
            "model_transformation": {
                "translation": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
            "view_frustum": {
                "near_plane": 0.1,
                "far_plane": 100,
                "vertical_field_of_view": 45,
            },
            "agent_state_model": {
                "agent_states": ["A", "B", "C"],
                "initial_agent_state": "A",
                "state_transition_map": [
                    {
                        "current_state": "A",
                        "transitions_to": ["B", "C"],
                        "next_state_weights": [0.4, 0.6],
                    },
                    {
                        "current_state": "B",
                        "transitions_to": ["A", "C"],
                        "next_state_weights": [0.1, 0.9],
                    },
                    {"current_state": "C", "transitions_to": ["A"]},
                ],
            },
        }

        LoadSchemaIntoMemory().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )
        ValidateJSONWithSchema().process(
            context, AGENT_DEF_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

    def test_json_valid_full_example(self) -> None:
        scene_rel_path = "agents_playground/agents/file/agent_def.example.json"
        agent_def_path = os.path.join(Path.cwd(), scene_rel_path)
        context = {}
        jfl = JSONFileLoader()
        assert jfl.load(
            context,
            AGENT_DEF_SCHEMA_PATH,
            agent_def_path,
            search_directories=search_dirs,
        )
        assert context["json_content"] is not None


class TestAgentDefinitionLoader:
    def test_stuff(self) -> None:
        scene_rel_path = "agents_playground/agents/file/agent_def.example.json"
        agent_def_path = os.path.join(Path.cwd(), scene_rel_path)
        loader = AgentDefinitionLoader()
        agent_def: AgentDefinition = loader.load(agent_def_path)
        assert isinstance(agent_def.agent_model, str)
        assert agent_def.agent_model == "path/to/a/model.obj"

        assert isinstance(agent_def.model_transformation, ModelTransformation)
        assert agent_def.model_transformation.translation == Vector3d(0, 0, 0)
        assert agent_def.model_transformation.rotation == Vector3d(0, 0, 0)
        assert agent_def.model_transformation.scale == Vector3d(1, 1, 1)

        assert isinstance(agent_def.view_frustum, Frustum3d)
        assert agent_def.view_frustum.near_plane_depth == 0.1
        assert agent_def.view_frustum.depth_of_field == 100
        assert agent_def.view_frustum.field_of_view == 45

        assert isinstance(agent_def.agent_state_model, Something)
        model: FsmAgentStateModel = agent_def.agent_state_model.unwrap()

        assert len(model.agent_states) == 5
        assert isinstance(model.agent_states, dict)
        assert model.initial_agent_state == model.agent_states["IDLE_STATE"]
        assert isinstance(model.state_transition_map, FuzzyAgentActionSelector)
