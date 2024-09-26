from collections.abc import Sequence
from enum import StrEnum
from typing import Any, Protocol

from agents_playground.fp import Maybe
from agents_playground.tasks.registry import TaskRegistry
from agents_playground.tasks.resources import TaskResourceRegistry, TaskResourceTracker
from agents_playground.tasks.tracker import TaskTracker
from agents_playground.tasks.types import (
    ResourceId,
    ResourceName,
    TaskLike,
    TaskName,
    TaskResource,
    TaskRunnerLike,
    TaskStatus,
)


class TaskGraphPhase(StrEnum):
    INITIALIZATION = "INITIALIZATION"
    FRAME_DRAW = "FRAME_DRAW"
    SHUTDOWN = "SHUTDOWN"


class TaskGraphError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TaskGraphLike(Protocol):
    task_registry: TaskRegistry
    resource_registry: TaskResourceRegistry
    task_tracker: TaskTracker
    resource_tracker: TaskResourceTracker
    task_runner: TaskRunnerLike

    def provision_task(self, name: TaskName, *args, **kwargs) -> TaskLike:
        """Provisions a task and adds it to the tracker.

        Args:
        - name: The name of the task to provision.
        - args: The positional arguments to pass to the TaskLike.
        - kwargs: The named arguments to pass to the TaskLike.

        Returns:
        The instance of the task that was provisioned.
        """
        ...

    def provision_resource(
        self, name: ResourceName, instance: Any | None = None, *args, **kwargs
    ) -> TaskResource: ...

    def get_resource(self, key: ResourceId | ResourceName) -> Maybe[TaskResource]: ...

    def clear(self) -> None:
        """
        Deletes all provisioned resources and tasks and removes all registrations.
        Basically, resets the task graph to be empty.
        """
        ...

    def tasks_with_status(
        self, filter: Sequence[TaskStatus]
    ) -> tuple[TaskLike, ...]: ...

    def check_if_blocked_tasks_are_ready(self) -> None:
        """
        Inspect all provisioned tasks with a status of INITIALIZED or BLOCKED to see if
        they're ready to run. If they are, then update the status to READY_FOR_ASSIGNMENT.

        Effects:
        - Tasks that are INITIALIZED but blocked have their status set to BLOCKED.
        - Tasks that are INITIALIZED or BLOCKED have their status set to READY_FOR_ASSIGNMENT.
        """
        ...

    def run_all_ready_tasks(self) -> None:
        """Run all tasks that have their status set to READY_FOR_ASSIGNMENT."""
        ...

    def run_until_done(self) -> None:
        """
        Continue to run tasks until they're all complete or the graph is blocked.

        Effects:
        - Calls check_if_blocked_tasks_are_ready to prompt tasks into ready status.
        - Runs tasks and pushes them into completed status.
        """
        ...
