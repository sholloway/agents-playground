from typing import Any

from agents_playground.loaders import JSONFileLoader, search_directories
from agents_playground.tasks.types import SimulationTasks

TASKS_SCHEMA_PATH = "agents_playground/tasks/file/tasks.schema.json"


class SimulationTasksLoader:
    def __init__(self):
        self._json_loader = JSONFileLoader()

    def load(self, tasks_file_path: str) -> SimulationTasks:
        loader_context: dict[str, Any] = {}
        self._json_loader.load(
            context=loader_context,
            schema_path=TASKS_SCHEMA_PATH,
            file_path=tasks_file_path,
            search_directories=search_directories(),
        )
        json_obj: dict = loader_context["json_content"]
        return SimulationTasks(**json_obj)
