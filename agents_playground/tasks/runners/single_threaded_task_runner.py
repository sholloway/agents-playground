from collections.abc import Sequence
from typing import Callable

from agents_playground.sys.logger import LoggingLevel, log_call, get_default_logger
from agents_playground.tasks.types import (
    ResourceDict,
    TaskErrorMsg,
    TaskGraphLike,
    TaskId,
    TaskInputs,
    TaskLike,
    TaskOutputs,
    TaskRunResult,
)


class TaskRunnerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SingleThreadedTaskRunner:
    @log_call(level=LoggingLevel.DEBUG)
    def run(
        self,
        task_graph: TaskGraphLike,
        tasks: Sequence[TaskLike],
        notify: Callable[[TaskId, TaskRunResult, TaskErrorMsg], None],
    ) -> None:
        for task in tasks:
            get_default_logger().debug(f"Attempting to run task {task.task_name}")
            try:
                inputs: TaskInputs = task_graph.collect_inputs_for(task.task_name)
                outputs: TaskOutputs = ResourceDict()
                task.action(task_graph, inputs, outputs)
                task_graph.provision_resources(outputs)
                notify(task.task_id, TaskRunResult.SUCCESS, "")
                get_default_logger().debug(f"Task {task.task_name} completed.")
            except Exception as e:
                get_default_logger().error(
                    f"An error occurred while trying to run task {task.task_name}."
                )
                get_default_logger().exception(e)
                raise TaskRunnerError(e)
