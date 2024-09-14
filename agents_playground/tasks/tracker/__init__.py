from collections.abc import Sequence
from operator import itemgetter
from agents_playground.core.task_scheduler import TaskId
from agents_playground.tasks.registry import TaskRegistry
from agents_playground.tasks.types import TaskDef, TaskLike, TaskName, TaskStatus


class TaskTrackerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TaskTracker:
    """
    Responsible for maintaining provisioned tasks.
    """

    def __init__(self) -> None:
        self._provisioned_tasks: list[TaskLike] = []
        self._task_id_index: dict[TaskId, int] = {}
        self._task_name_index: dict[TaskName, int] = {}

    def clear(self) -> None:
        self._provisioned_tasks.clear()
        self._task_id_index.clear()

    def track(self, task: TaskLike) -> TaskId:
        if task.task_id in self._provisioned_tasks:
            raise TaskTrackerError(f"The task {task.task_id} is already being tracked.")
        self._provisioned_tasks.append(task)
        task_index = len(self._provisioned_tasks) - 1
        self._task_id_index[task.task_id] = task_index
        self._task_name_index[task.task_name] = task_index
        return task.task_id

    def filter_by_status(self, filter: Sequence[TaskStatus]) -> tuple[TaskLike, ...]:
        return tuple(
            [task for task in self._provisioned_tasks if task.status in filter]
        )

    def filter_by_name(self, filter: Sequence[TaskName]) -> tuple[TaskLike, ...]:
        task_indices = itemgetter(*filter)(self._task_name_index)
        result = itemgetter(*task_indices)(self._provisioned_tasks)
        if not isinstance(result, tuple):
            result = tuple(result)
        return result

    def collect_by_name(self, filter: Sequence[TaskName]) -> tuple[TaskLike, ...]:
        """
        Similar to filter_by_name but raises an error if task is associated with a provided name.
        """
        for task_name in filter:
            if task_name not in self._task_name_index:
                raise TaskTrackerError(
                    f"There is no provisioned task being tracked with the name {task_name}."
                )

        # Get all of the tasks by their name.
        return self.filter_by_name(filter)

    def check_if_ready(self, task_registry: TaskRegistry) -> None:
        """
        Given a task_registry, inspect all tasks with a status of
        INITIALIZED or BLOCKED to see if they're ready to run.
        If they are, then update the status to READY_FOR_ASSIGNMENT.

        Effects:
        - Tasks that are INITIALIZED but blocked have their status set to BLOCKED.
        - Tasks that are INITIALIZED or BLOCKED have their status set to READY_FOR_ASSIGNMENT.
        """
        status_filter = (TaskStatus.INITIALIZED, TaskStatus.BLOCKED)
        tasks_to_check = self.filter_by_status(status_filter)
        for task in tasks_to_check:
            # Get the task's definition.
            task_def: TaskDef = task_registry[task.task_name]

            # Get the provisioned before tasks.
            before_tasks: tuple[TaskLike, ...] = self.collect_by_name(
                task_def.required_before_tasks
            )

            # Did all the before tasks run?
            all_before_tasks_done = all([task.status == TaskStatus.COMPLETE for task in before_tasks])

            # Are the required inputs allocated?
            task_def.inputs
        

    # def task_graph(self) -> TaskGraph:
    #     graph = TaskGraph()
    #     for task in self._provisioned_tasks:
    #         pass
    #         # task.required_before_tasks
    #         # graph.
    #     return graph

    def __getitem__(self, key: TaskId) -> TaskLike:
        """Finds a TaskLike definition by its alias."""
        index = self._task_id_index[key]
        return self._provisioned_tasks[index]

    def __len__(self) -> int:
        return len(self._provisioned_tasks)

    def __contains__(self, key: TaskId) -> bool:
        return key in self._task_id_index


_task_tracker = TaskTracker()


def global_task_tracker() -> TaskTracker:
    return _task_tracker
