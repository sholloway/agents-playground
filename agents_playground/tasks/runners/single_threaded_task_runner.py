from collections.abc import Sequence
from typing import Callable

from agents_playground.fp import Maybe
from agents_playground.sys.logger import LoggingLevel, log_call, get_default_logger
from agents_playground.tasks.types import (
    ResourceDict,
    ResourceName,
    TaskDef,
    TaskErrorMsg,
    TaskGraphLike,
    TaskId,
    TaskInputs,
    TaskLike,
    TaskOutputs,
    TaskResource,
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
                task_def: TaskDef = task_graph.task_def(task.task_name)
                if task_def.run_if():
                    inputs, outputs = self._prepare_task(task_graph, task)
                    task.action(task_graph, inputs, outputs)
                    task_graph.provision_resources(outputs)
                    self._validate_task_outputs(task_graph, task_def)
                    notify(task.task_id, TaskRunResult.SUCCESS, "")
                    get_default_logger().debug(f"Task {task.task_name} completed.")
                else:
                    # The task is not permitted to run. Mark it as skipped.
                    notify(task.task_id, TaskRunResult.SKIPPED, "")
            except Exception as e:
                get_default_logger().error(
                    f"An error occurred while trying to run task {task.task_name}."
                )
                get_default_logger().exception(e)
                raise TaskRunnerError(e)

    def _prepare_task(
        self, task_graph: TaskGraphLike, task: TaskLike
    ) -> tuple[TaskInputs, TaskOutputs]:
        inputs: TaskInputs = task_graph.collect_inputs_for(task.task_name)
        outputs: TaskOutputs = ResourceDict()
        return inputs, outputs

    def _validate_task_outputs(
        self, task_graph: TaskGraphLike, task_def: TaskDef
    ) -> None:
        """Verify that all of the expected outputs were set."""
        missing_resources: list[ResourceName] = []
        for resource_name in task_def.outputs:
            resource: Maybe[TaskResource] = task_graph.resource(resource_name)
            if not resource.is_something():
                missing_resources.append(resource_name)
        if len(missing_resources) > 0:
            error_msg = f"Task {task_def.name} did not register all expected outputs. Outputs missing: {missing_resources}."
            raise TaskRunnerError(error_msg)
