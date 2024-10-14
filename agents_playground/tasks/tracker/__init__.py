from collections.abc import Sequence
from operator import itemgetter
from typing import Iterator

from agents_playground.tasks.types import TaskId, TaskLike, TaskName, TaskStatus


class TaskTrackerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TaskTracker:
    """
    Responsible for maintaining provisioned tasks.
    """

    def __init__(self) -> None:
        self._provisioned_tasks: list[TaskLike | None] = []
        self._task_id_index: dict[TaskId, int] = {}
        self._task_name_index: dict[TaskName, int] = {}

    def clear(self) -> None:
        self._task_id_index.clear()
        self._task_name_index.clear()
        self._provisioned_tasks.clear()

    def track(self, task: TaskLike) -> TaskId:
        if task.task_id in self._provisioned_tasks:
            raise TaskTrackerError(f"The task {task.task_id} is already being tracked.")
        self._provisioned_tasks.append(task)
        task_index = len(self._provisioned_tasks) - 1
        self._task_id_index[task.task_id] = task_index
        self._task_name_index[task.task_name] = task_index
        return task.task_id

    def filter_by_status(
        self, filter: Sequence[TaskStatus], inclusive: bool = True
    ) -> tuple[TaskLike, ...]:
        if inclusive:
            tasks = [task for task in self._provisioned_tasks if task.status in filter]
        else:
            tasks = [
                task for task in self._provisioned_tasks if task.status not in filter
            ]
        return tuple(tasks)

    def filter_by_name(self, filter: Sequence[TaskName]) -> tuple[TaskLike, ...]:
        task_indices = itemgetter(*filter)(self._task_name_index)
        if not isinstance(task_indices, tuple):
            task_indices = (task_indices,)

        result: tuple[TaskLike, ...] | TaskLike = itemgetter(*task_indices)(
            self._provisioned_tasks
        )
        if not isinstance(result, tuple):
            result = (result,)
        return result

    def collect_by_name(self, filter: Sequence[TaskName]) -> tuple[TaskLike, ...]:
        """
        Similar to filter_by_name but raises an error if task is associated with a provided name.
        """
        if len(filter) == 0:
            return tuple()

        for task_name in filter:
            if task_name not in self._task_name_index:
                raise TaskTrackerError(
                    f"There is no provisioned task being tracked with the name {task_name}."
                )

        # Get all of the tasks by their name.
        return self.filter_by_name(filter)

    def release(self, task_ids: Sequence[TaskId]) -> None:
        for task_id in task_ids:
            if task_id not in self._task_id_index:
                # Bad task ID, skip and continue.
                continue

            # Find the location of the task and fetch it.
            task_index = self._task_id_index[task_id]
            task = self[task_id]

            # Remove the task from the tracker.
            # Note: Assigning None to the _provisioned_tasks[task_index] so the indexes
            # don't have to be recalculated. This may prove problematic for large graphs.
            del self._task_name_index[task.task_name]
            del self._task_id_index[task_id]
            self._provisioned_tasks[task_index] = None

    def __getitem__(self, key: TaskId | TaskName) -> TaskLike:
        """Finds a TaskLike definition by its alias."""
        if isinstance(key, int):
            index = self._task_id_index[key]
        elif isinstance(key, str):
            index = self._task_name_index[key]
        task = self._provisioned_tasks[index]
        if task is None:
            raise TaskTrackerError("The task with key {key} was released already.")
        return task

    def __len__(self) -> int:
        return len(self._provisioned_tasks)

    def __contains__(self, key: TaskId) -> bool:
        return key in self._task_id_index

    def __iter__(self) -> Iterator:
        """Enables iterating over all the provisioned tasks."""
        return self._provisioned_tasks.__iter__()
