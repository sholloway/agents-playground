from collections.abc import Sequence
import sys
from typing import Iterator


from agents_playground.containers.types import MultiIndexedContainerLike
from agents_playground.sys.profile_tools import total_size

from agents_playground.tasks.types import (
    TaskId,
    TaskLike,
    TaskName,
    TaskStatus,
    TaskTrackerLike,
)


class TaskTrackerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TaskTracker(TaskTrackerLike):
    """
    Responsible for maintaining provisioned tasks.
    """

    def __init__(self, indexer: MultiIndexedContainerLike) -> None:
        super().__init__()
        self._indexer = indexer

    def clear(self) -> None:
        self._indexer.clear()

    def track(self, tasks: TaskLike | Sequence[TaskLike]) -> None:
        if isinstance(tasks, Sequence):
            for task in tasks:
                self._indexer.track(task, task.id, task.name)
        else:
            self._indexer.track(tasks, tasks.id, tasks.name)

    def filter_by_status(
        self, filter: Sequence[TaskStatus], inclusive: bool = True
    ) -> tuple[TaskLike, ...]:
        return self._indexer.filter("status", filter, inclusive)

    def filter_by_name(self, filter: Sequence[TaskName]) -> tuple[TaskLike, ...]:
        return self._indexer.filter("name", filter)

    def collect_by_name(self, filter: Sequence[TaskName]) -> tuple[TaskLike, ...]:
        """
        Similar to filter_by_name but raises an error if task is associated with a provided name.
        """
        if len(filter) == 0:
            return tuple()

        for task_name in filter:
            if task_name not in self._indexer:
                raise TaskTrackerError(
                    f"There is no provisioned task being tracked with the name {task_name}."
                )

        # Get all of the tasks by their name.
        return self.filter_by_name(filter)

    def release(self, task_ids: Sequence[TaskId]) -> int:
        return self._indexer.release(task_ids)

    def __getitem__(self, key: TaskId | TaskName) -> TaskLike:
        """Finds a TaskLike definition by its alias."""
        return self._indexer[key]

    def __len__(self) -> int:
        return len(self._indexer)

    def __contains__(self, key: TaskId | TaskName) -> bool:
        return key in self._indexer

    def __iter__(self) -> Iterator:
        """Enables iterating over all the provisioned tasks."""
        return self._indexer.__iter__()

    def __sizeof__(self) -> int:
        base_size: int = sys.getsizeof(super())
        return base_size + total_size(self._indexer)
