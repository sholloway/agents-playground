from collections.abc import Sequence
from typing import Callable

from agents_playground.containers.attr_dict import AttrDict
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.fp import Maybe
from agents_playground.sys.logger import LoggingLevel, log_call, get_default_logger
from agents_playground.tasks.types import (
    ResourceName,
    TaskDef,
    TaskErrorMsg,
    TaskGraphLike,
    TaskId,
    TaskInputs,
    TaskLike,
    TaskOutputs,
    TaskResource,
    TaskRunHistory,
    TaskRunResult,
    TaskRunStep,
    TaskStatus,
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
    ) -> TaskRunHistory:
        history: list[TaskRunStep] = []
        run_start = TimeUtilities.perf_time_now_ns()
        for task in tasks:
            get_default_logger().debug(f"Attempting to run task {task.name}")
            try:
                task_def: TaskDef = task_graph.task_def(task.name)
                if task_def.run_if():
                    inputs, outputs = self._prepare_task(task_graph, task)
                    start_time = TimeUtilities.perf_time_now_ns()
                    task.action(task_graph, inputs, outputs)
                    end_time = TimeUtilities.perf_time_now_ns()
                    task_graph.provision_resources(outputs)
                    self._validate_task_outputs(task_graph, task_def)
                    history.append(
                        TaskRunStep(
                            id=task.id,
                            name=task.name,
                            started=start_time,
                            finished=end_time,
                            status=TaskStatus.COMPLETE,
                            produced=tuple(outputs.keys()),
                        )
                    )
                    notify(task.id, TaskRunResult.SUCCESS, "")
                    get_default_logger().debug(f"Task {task.name} completed.")
                else:
                    # The task is not permitted to run. Mark it as skipped.
                    notify(task.id, TaskRunResult.SKIPPED, "")
                    history.append(
                        TaskRunStep(
                            id=task.id,
                            name=task.name,
                            started=-1,
                            finished=-1,
                            status=TaskStatus.SKIPPED,
                            produced=tuple(),
                        )
                    )
            except Exception as e:
                get_default_logger().error(
                    f"An error occurred while trying to run task {task.name}."
                )
                get_default_logger().exception(e)
                raise TaskRunnerError(e)
        run_end = TimeUtilities.perf_time_now_ns()
        return TaskRunHistory(steps=tuple(history), started=run_start, finished=run_end)

    def _prepare_task(
        self, task_graph: TaskGraphLike, task: TaskLike
    ) -> tuple[TaskInputs, TaskOutputs]:
        inputs: TaskInputs = task_graph.collect_inputs_for(task.name)
        outputs: TaskOutputs = AttrDict()
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
