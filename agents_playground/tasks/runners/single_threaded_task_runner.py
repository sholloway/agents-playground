from collections.abc import Sequence
from typing import Callable

from agents_playground.sys.logger import log_call, get_default_logger
from agents_playground.tasks.types import TaskErrorMsg, TaskId, TaskLike, TaskRunResult

class TaskRunnerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class SingleThreadedTaskRunner:
    @log_call
    def run(
        self,
        tasks: Sequence[TaskLike],
        notify: Callable[[TaskId, TaskRunResult, TaskErrorMsg], None],
    ) -> None:
        for task in tasks:
            get_default_logger().info(f"Attempting to run task {task.task_name}")
            try:
                task.action(*task.args, **task.kwargs)
                notify(task.task_id, TaskRunResult.SUCCESS, "")
                get_default_logger().info(f"Task {task.task_name} completed.")
            except Exception as e:
                get_default_logger().error(f"An error occurred while trying to run task {task.task_name}.")
                get_default_logger().exception(e)
                raise TaskRunnerError(e)
