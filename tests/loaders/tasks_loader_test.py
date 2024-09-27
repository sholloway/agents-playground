import os
from pathlib import Path

from jsonschema import ValidationError
import pytest

from agents_playground.loaders import (
    JSONFileLoader,
    LoadSchemaIntoMemory,
    ValidateJSONWithSchema,
    ValidateSchema,
    search_directories,
)
from agents_playground.loaders.tasks_loader import (
    TASKS_SCHEMA_PATH,
    SimulationTasksLoader,
)

search_dirs = search_directories()
tasks_rel_path = "agents_playground/tasks/file/tasks_example.json"
tasks_path = os.path.join(Path.cwd(), tasks_rel_path)


class TestTasksLoader:
    def test_valid_schema(self) -> None:
        context = {}
        LoadSchemaIntoMemory().process(
            context, TASKS_SCHEMA_PATH, "", search_directories=search_dirs
        )
        ValidateSchema().process(
            context, TASKS_SCHEMA_PATH, "", search_directories=search_dirs
        )

    def test_initial_tasks_is_required(self) -> None:
        context = {}
        context["json_content"] = {}
        LoadSchemaIntoMemory().process(
            context, TASKS_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context, TASKS_SCHEMA_PATH, file_path="", search_directories=search_dirs
            )
        assert "'initial_tasks' is a required property" in str(err.value)

    def test_per_frame_tasks_is_required(self) -> None:
        context = {}
        context["json_content"] = {"initial_tasks": []}
        LoadSchemaIntoMemory().process(
            context, TASKS_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context, TASKS_SCHEMA_PATH, file_path="", search_directories=search_dirs
            )
        assert "'per_frame_tasks' is a required property" in str(err.value)

    def test_render_tasks_is_required(self) -> None:
        context = {}
        context["json_content"] = {"initial_tasks": [], "per_frame_tasks": []}
        LoadSchemaIntoMemory().process(
            context, TASKS_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context, TASKS_SCHEMA_PATH, file_path="", search_directories=search_dirs
            )
        assert "'render_tasks' is a required property" in str(err.value)

    def test_shutdown_tasks_is_required(self) -> None:
        context = {}
        context["json_content"] = {
            "initial_tasks": [],
            "per_frame_tasks": [],
            "render_tasks": [],
        }
        LoadSchemaIntoMemory().process(
            context, TASKS_SCHEMA_PATH, file_path="", search_directories=search_dirs
        )

        with pytest.raises(ValidationError) as err:
            ValidateJSONWithSchema().process(
                context, TASKS_SCHEMA_PATH, file_path="", search_directories=search_dirs
            )
        assert "'shutdown_tasks' is a required property" in str(err.value)

    def test_json_valid_full_example(self) -> None:
        context = {}
        jfl = JSONFileLoader()
        assert jfl.load(
            context, TASKS_SCHEMA_PATH, tasks_path, search_directories=search_dirs
        )
        assert context["json_content"] is not None

    def test_load_tasks(self) -> None:
        loader = SimulationTasksLoader()
        sim_tasks = loader.load(tasks_path)

        assert sim_tasks is not None
        assert len(sim_tasks.initial_tasks) == 12
        assert "load_textures" in sim_tasks.initial_tasks

        assert len(sim_tasks.per_frame_tasks) == 4
        assert "update_agents" in sim_tasks.per_frame_tasks

        assert len(sim_tasks.render_tasks) == 11
        assert "bind_camera_data" in sim_tasks.render_tasks

        assert len(sim_tasks.shutdown_tasks) == 2
        assert "end_simulation" in sim_tasks.shutdown_tasks
