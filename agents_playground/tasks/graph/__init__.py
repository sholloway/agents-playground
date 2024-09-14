from dataclasses import dataclass

from agents_playground.tasks.types import ResourceId, TaskId, TaskName


@dataclass
class TaskGraphNode:
    """
    Represents a task that has been provisioned and could possibly be run.
    """
    task_id: TaskId # The ID of the provisioned task.
    task_name: TaskName # The name that was used to provision the task. Used for debugging.
    parent_ids: list[TaskId] # The list of tasks that must run before this task.
    inputs: list[ResourceId] # The list of inputs that must be allocated before the this task can run.

class TaskGraph:
    """
    Represents a collection of interdependent tasks. Loops are not permitted.
    """
    def __init__(self) -> None:
        self._ready_to_run: list[TaskId] = []
        self._blocked_to_run: list[TaskId] = []

    def ready_to_run(self, id: TaskId) -> None:
        if id not in self._ready_to_run:
            self._ready_to_run.append(id)