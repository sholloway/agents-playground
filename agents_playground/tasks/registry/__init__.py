from itertools import chain
from typing import Iterator
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.sys.logger import get_default_logger
from agents_playground.tasks.types import (
    TaskDef,
    TaskLike,
    TaskName,
    TaskRegistryLike,
    TaskStatus,
)


class TaskRegistryError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TaskRegistry:
    """
    Responsible for maintaining a registry of tasks that can be provisioned.
    When a task is provisioned it is stored in the TaskRegistry.
    """

    def __init__(self) -> None:
        # Storage and indices for task type declarations
        self._registered_tasks: list[TaskDef] = []
        self._aliases_index: dict[TaskName, int] = {}
        self._task_counter: Counter[int] = CounterBuilder.count_up_from_zero()

    def register(self, alias: str, task_def: TaskDef) -> None:
        """Alternative to tr[alias] = task_def."""
        self[alias] = task_def

    def task_names(self) -> tuple[TaskName, ...]:
        return tuple(self._aliases_index.keys())

    def clear(self) -> None:
        self._aliases_index.clear()
        self._registered_tasks.clear()

    def provision(self, alias: str) -> TaskLike:
        if alias not in self._aliases_index:
            raise TaskRegistryError(
                f"Attempted to provision a task that was not registered. Could not find task alias {alias}."
            )
        task_def_index = self._aliases_index[alias]
        task_def = self._registered_tasks[task_def_index]

        # Typically creates an instance of GenericTask.
        task: TaskLike = task_def.type()

        task.task_name = alias
        task.task_id = self._task_counter.increment()
        task.status = TaskStatus.INITIALIZED
        task.action = task_def.action

        return task

    def __iter__(self) -> Iterator:
        """Enables iterating over all the registered tasks."""
        return self._registered_tasks.__iter__()

    def add_requirement(
        self, before_tasks: tuple[TaskName, ...], later_tasks: tuple[TaskName, ...]
    ) -> None:
        """
        Set a task dependency. Task A (B, C,...) must run before task X, (Y, Z).

        Args:
        - before_tasks: The list of tasks that must run before the later tasks.
        - later_tasks: The list of tasks that can run after the list of tasks in the before tuple.
        """
        # Verify that all tasks are in the registry.
        for task_name in chain(before_tasks, later_tasks):
            if task_name not in self._aliases_index:
                raise TaskRegistryError(
                    f"Attempted to add a requirement on a task that is not registered.\nThe task name {task_name} is not associated with a registered task."
                )

        # Add the before tasks as requirements to the later tasks.
        for later_task_name in later_tasks:
            later_task: TaskDef = self[later_task_name]
            later_task.required_before_tasks.extend(before_tasks)

    @property
    def provisioned_tasks_count(self) -> int:
        return self._task_counter.value()

    def __setitem__(self, key: str, value: TaskDef) -> None:
        if key in self._aliases_index:
            raise TaskRegistryError(
                f"The alias {key} is already assigned to a Task definition."
            )
        if value in self._registered_tasks:
            index = self._registered_tasks.index(value)
        else:
            self._registered_tasks.append(value)
            index = len(self._registered_tasks) - 1
        self._aliases_index[key] = index

    def __getitem__(self, key: TaskName) -> TaskDef:
        """Finds a TaskLike definition by its alias."""
        index = self._aliases_index[key]
        return self._registered_tasks[index]

    def __len__(self) -> int:
        return len(self._aliases_index)

    def __contains__(self, key: str) -> bool:
        """Enables 'my_alias' in task_registry."""
        return key in self._aliases_index


_task_registry: TaskRegistry = TaskRegistry()


def global_task_registry() -> TaskRegistryLike:
    return _task_registry
