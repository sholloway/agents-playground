from collections.abc import Sequence
from dataclasses import dataclass, field
import logging

from agents_playground.core.task_scheduler import TaskId
from agents_playground.sys.logger import get_default_logger
from agents_playground.tasks.registry import TaskRegistry, global_task_registry
from agents_playground.tasks.resources import (
    TaskResourceRegistry,
    TaskResourceTracker,
    global_task_resource_registry,
)
from agents_playground.tasks.runners.single_threaded_task_runner import (
    SingleThreadedTaskRunner,
)
from agents_playground.tasks.tracker import TaskTracker
from agents_playground.tasks.types import (
    ResourceName,
    TaskDef,
    TaskErrorMsg,
    TaskLike,
    TaskName,
    TaskResourceLike,
    TaskRunResult,
    TaskRunnerLike,
    TaskStatus,
)

logger: logging.Logger = get_default_logger()


@dataclass
class TaskGraph:
    """
    Represents a collection of interdependent tasks. Loops are not permitted.
    """

    task_registry: TaskRegistry = field(default_factory=lambda: global_task_registry())

    resource_registry: TaskResourceRegistry = field(
        default_factory=lambda: global_task_resource_registry()
    )

    task_tracker: TaskTracker = field(default_factory=lambda: TaskTracker())

    task_resource_tracker: TaskResourceTracker = field(
        default_factory=lambda: TaskResourceTracker()
    )

    task_runner: TaskRunnerLike = field(
        default_factory=lambda: SingleThreadedTaskRunner()
    )

    def provision_task(self, name: TaskName, *args, **kwargs) -> TaskLike:
        """Provisions a task and adds it to the tracker.

        Args:
        - name: The name of the task to provision.
        - args: The positional arguments to pass to the TaskLike.
        - kwargs: The named arguments to pass to the TaskLike.

        Returns:
        The instance of the task that was provisioned.
        """
        kwargs["task_graph"] = self  # inject the task_graph.
        task = self.task_registry.provision(name, *args, **kwargs)
        self.task_tracker.track(task)
        return task
    
    def provision_resource(self, name: ResourceName, *args, **kwargs) -> TaskResourceLike:
        resource: TaskResourceLike = self.resource_registry.provision(name, *args, **kwargs)
        self.task_resource_tracker.track(resource)
        return resource

    def tasks_with_status(self, filter: Sequence[TaskStatus]) -> tuple[TaskLike, ...]:
        return self.task_tracker.filter_by_status(filter)

    def check_if_blocked_tasks_are_ready(self) -> None:
        """
        Inspect all provisioned tasks with a status of INITIALIZED or BLOCKED to see if
        they're ready to run. If they are, then update the status to READY_FOR_ASSIGNMENT.

        Effects:
        - Tasks that are INITIALIZED but blocked have their status set to BLOCKED.
        - Tasks that are INITIALIZED or BLOCKED have their status set to READY_FOR_ASSIGNMENT.
        """
        status_filter = (TaskStatus.INITIALIZED, TaskStatus.BLOCKED)
        tasks_to_check: tuple[TaskLike, ...] = self.task_tracker.filter_by_status(
            status_filter
        )

        for task in tasks_to_check:
            # Get the task's definition.
            task_def: TaskDef = self.task_registry[task.task_name]

            # Get the provisioned before tasks.
            before_tasks: tuple[TaskLike, ...] = self.task_tracker.collect_by_name(
                task_def.required_before_tasks
            )

            # Did all the before tasks run?
            all_before_tasks_are_complete = all(
                [task.status == TaskStatus.COMPLETE for task in before_tasks]
            )

            # TODO: Check that the required inputs have been allocated.
            all_inputs_are_allocated = True

            if all_before_tasks_are_complete and all_inputs_are_allocated:
                task.status = TaskStatus.READY_FOR_ASSIGNMENT
            else:
                task.status = TaskStatus.BLOCKED

    def run_all_ready_tasks(self) -> None:
        """Run all tasks that have their status set to READY_FOR_ASSIGNMENT."""
        ready_tasks = self.task_tracker.filter_by_status(
            (TaskStatus.READY_FOR_ASSIGNMENT,)
        )
        self.task_runner.run(ready_tasks, self._handle_task_done)

    def run_until_done(self) -> None:
        """
        Continue to run tasks until they're all complete or the graph is blocked.

        Effects:
        - Calls check_if_blocked_tasks_are_ready to prompt tasks into ready status.
        - Runs tasks and pushes them into completed status.
        """
        still_work_to_do: bool = True
        while still_work_to_do:
            self.run_all_ready_tasks()
            self.check_if_blocked_tasks_are_ready()
            still_work_to_do = self._work_to_do()

    def is_valid(self) -> tuple[bool, str]:
        """
        Determines if the provisioned tasks and resources form a valid task graph that can be run.

        A valid task graph is one that:
        - Based on the inter-task relationships all tasks will eventually be able to run.

        Effects:
        -
        """
        ...

    def _work_to_do(self) -> bool:
        """
        Returns true if there are any tasks with a status of READY_FOR_ASSIGNMENT.
        """
        return (
            len(self.task_tracker.filter_by_status((TaskStatus.READY_FOR_ASSIGNMENT,)))
            > 0
        )

    def _handle_task_done(
        self, taskId: TaskId, result: TaskRunResult, error_msg: TaskErrorMsg
    ) -> None:
        if result == TaskRunResult.SUCCESS:
            self.task_tracker[taskId].status = TaskStatus.COMPLETE
        else:
            failed_task = self.task_tracker[taskId]
            logger.error(f"Task {failed_task.task_name} failed to run.\n{error_msg}")
