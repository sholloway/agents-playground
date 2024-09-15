from collections.abc import Sequence
from typing import Callable

from agents_playground.tasks.types import TaskErrorMsg, TaskId, TaskLike, TaskRunResult


class SingleThreadedTaskRunner:
    def run(
        self,
        tasks: Sequence[TaskLike],
        notify: Callable[[TaskId, TaskRunResult, TaskErrorMsg], None],
    ) -> None:
        for task in tasks:
            task.task_ref(*task.args, **task.kwargs)
            notify(task.task_id, TaskRunResult.SUCCESS, "")