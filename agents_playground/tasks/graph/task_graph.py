from collections.abc import Sequence
from operator import itemgetter
from typing import Any

from agents_playground.fp import Maybe
from agents_playground.sys.logger import get_default_logger, log_call
from agents_playground.tasks.graph.types import TaskGraphError
from agents_playground.tasks.registry import global_task_registry
from agents_playground.tasks.resources import (
    TaskResourceTracker,
    global_task_resource_registry,
)
from agents_playground.tasks.runners.single_threaded_task_runner import (
    SingleThreadedTaskRunner,
)
from agents_playground.tasks.tracker import TaskTracker
from agents_playground.tasks.types import (
    ResourceDict,
    ResourceId,
    ResourceName,
    TaskDef,
    TaskErrorMsg,
    TaskId,
    TaskInputs,
    TaskLike,
    TaskName,
    TaskRegistryLike,
    TaskResource,
    TaskResourceDef,
    TaskResourceRegistryLike,
    TaskResourceTrackerLike,
    TaskRunResult,
    TaskRunnerLike,
    TaskStatus,
    TaskTrackerLike,
)

logger = get_default_logger()


# TODO: Simplify the TaskGraph API. I don't want to do things like tg.resource_tracker["my_resource"].
# It should be closer to something like:
#  - tg.allocate_resource("my_resource.", instance=...)
#  - tg.get_resource("my_resource.") -> ResourceType
#  - tg.unwrap_resource("my_resource") -> Any
#  - tg.unwrap_resources(tag="resources") -> dict[name, Any]


class TaskGraph:
    """
    Represents a collection of interdependent tasks. Loops are not permitted.
    """

    def __init__(
        self,
        task_registry: TaskRegistryLike | None = None,
        resource_registry: TaskResourceRegistryLike | None = None,
        task_tracker: TaskTrackerLike | None = None,
        resource_tracker: TaskResourceTrackerLike | None = None,
        task_runner: TaskRunnerLike | None = None,
    ) -> None:
        self._task_registry: TaskRegistryLike = (
            global_task_registry() if task_registry is None else task_registry
        )
        self._resource_registry: TaskResourceRegistryLike = (
            global_task_resource_registry()
            if resource_registry is None
            else resource_registry
        )
        self._task_tracker: TaskTrackerLike = (
            TaskTracker() if task_tracker is None else task_tracker
        )
        self._resource_tracker: TaskResourceTrackerLike = (
            TaskResourceTracker() if resource_tracker is None else TaskResourceTracker()
        )

        self._task_runner: TaskRunnerLike = (
            SingleThreadedTaskRunner() if task_runner is None else task_runner
        )

    def provision_task(self, name: TaskName) -> TaskLike:
        """Provisions a task and adds it to the tracker.

        Args:
        - name: The name of the task to provision.

        Returns:
        The instance of the task that was provisioned.
        """
        try:
            task = self._task_registry.provision(name)
            self._task_tracker.track(task)
        except Exception as e:
            logger.error(
                f"An error occurred while attempting to provision an instance of task {name}."
            )
            logger.exception(e)
            raise TaskGraphError(f"Failed to provision task {name}")
        return task

    def provision_resource(
        self, name: ResourceName, instance: Any | None = None, *args, **kwargs
    ) -> TaskResource:
        resource: TaskResource = self._resource_registry.provision(
            name, instance, *args, **kwargs
        )
        self._resource_tracker.track(resource)
        return resource

    def provision_resources(self, resources: ResourceDict) -> None:
        """
        Given a collection of resources, provision them in the
        resource tracker with the provided instances.
        """
        for resource_name, resource in resources.items():
            self.provision_resource(name=resource_name, instance=resource)

    def resource_def(self, key: ResourceName) -> Maybe[TaskResourceDef]:
        """
        Find a resource's registered definition by its name.
        Returns an instance of Nothing if a definition isn't found.
        """
        return self._resource_registry.get(key)

    def resource(self, key: ResourceId | ResourceName) -> Maybe[TaskResource]:
        """
        Get a tracked, provisioned resource. If the resource isn't tracked then
        an instance of Nothing is returned.
        """
        return self._resource_tracker.get(key)

    def unwrap_tracked_resource(self, key: ResourceId | ResourceName) -> Any:
        task_resource: TaskResource = self._resource_tracker[key]
        return task_resource.resource.unwrap_or_throw(
            f"The resource {key} could not be found in the TaskGraph's resource tracker."
        )

    def clear(self) -> None:
        """
        Deletes all provisioned resources and tasks and removes all registrations.
        Basically, resets the task graph to be empty.
        """
        self._resource_tracker.clear()
        self._task_tracker.clear()
        self._resource_registry.clear()
        self._task_registry.clear()

    def task_def(self, key: TaskName) -> TaskDef:
        """
        Find a task definition by its name.
        """
        return self._task_registry[key]

    def task(self, key: TaskId | TaskName) -> TaskLike:
        """
        Find a provisioned task by its ID or name.
        """
        return self._task_tracker[key]

    def tasks_with_status(self, filter: Sequence[TaskStatus]) -> tuple[TaskLike, ...]:
        return self._task_tracker.filter_by_status(filter)

    def tasks_without_status(
        self, filter: Sequence[TaskStatus]
    ) -> tuple[TaskLike, ...]:
        return self._task_tracker.filter_by_status(filter, inclusive=False)

    def check_if_blocked_tasks_are_ready(self) -> None:
        """
        Inspect all provisioned tasks with a status of INITIALIZED or BLOCKED to see if
        they're ready to run. If they are, then update the status to READY_FOR_ASSIGNMENT.

        Effects:
        - Tasks that are INITIALIZED but blocked have their status set to BLOCKED.
        - Tasks that are INITIALIZED or BLOCKED have their status set to READY_FOR_ASSIGNMENT.
        """
        status_filter = (TaskStatus.INITIALIZED, TaskStatus.BLOCKED)
        tasks_to_check: tuple[TaskLike, ...] = self._task_tracker.filter_by_status(
            status_filter
        )

        for task in tasks_to_check:
            # Get the task's definition.
            task_def: TaskDef = self._task_registry[task.task_name]

            # If the task has a conditional requirement, run that
            # to determine it the task is permitted to run.
            # Skip the rest of the checks if the bound run_if
            # function returns False.
            if not task_def.run_if():
                # Tasks that fail their run_if check will not be run
                # so mark it as complete.
                task.status = TaskStatus.COMPLETE
                logger.info(
                    f"The task {task.task_name} was not run because its run_if check {task_def.run_if.__qualname__} evaluated to False."
                )
                continue

            # Get the provisioned before tasks.
            before_tasks: tuple[TaskLike, ...] = self._task_tracker.collect_by_name(
                task_def.required_before_tasks
            )

            # Did all the before tasks run?
            all_before_tasks_are_complete = all(
                [task.status == TaskStatus.COMPLETE for task in before_tasks]
            )

            # Check that the required inputs have been allocated.
            allocated_inputs = [
                required_input in self._resource_tracker
                for required_input in task_def.inputs
            ]
            all_inputs_are_allocated = all(allocated_inputs)

            if all_before_tasks_are_complete and all_inputs_are_allocated:
                task.status = TaskStatus.READY_FOR_ASSIGNMENT
                task.waiting_on.clear()
            else:
                task.status = TaskStatus.BLOCKED
                task.waiting_on = {
                    "tasks": [
                        task.task_name
                        for task in before_tasks
                        if task.status != TaskStatus.COMPLETE
                    ],
                    "inputs": [
                        required_input
                        for required_input in task_def.inputs
                        if required_input not in self._resource_tracker
                    ],
                }

    def run_all_ready_tasks(self) -> None:
        """Run all tasks that have their status set to READY_FOR_ASSIGNMENT."""
        ready_tasks = self._task_tracker.filter_by_status(
            (TaskStatus.READY_FOR_ASSIGNMENT,)
        )
        self._task_runner.run(
            task_graph=self, tasks=ready_tasks, notify=self._handle_task_done
        )

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

    def collect_inputs_for(self, task_name: TaskName) -> TaskInputs:
        """
        Collects all of the provisioned input resources for a task.
        """
        task_def = self._task_registry[task_name]

        results = itemgetter(*task_def.inputs)(self._resource_tracker)
        input_resources: tuple[TaskResource] = (
            results if isinstance(results, tuple) else (results,)
        )

        inputs = {r.resource_name: r.resource.unwrap() for r in input_resources}
        return ResourceDict(inputs)

    def _work_to_do(self) -> bool:
        """
        Returns true if there are any tasks with a status of READY_FOR_ASSIGNMENT.
        """
        return (
            len(self._task_tracker.filter_by_status((TaskStatus.READY_FOR_ASSIGNMENT,)))
            > 0
        )

    def _handle_task_done(
        self, taskId: TaskId, result: TaskRunResult, error_msg: TaskErrorMsg
    ) -> None:
        match result:
            case TaskRunResult.SUCCESS:
                self._task_tracker[taskId].status = TaskStatus.COMPLETE
            case TaskRunResult.FAILED:
                self._task_tracker[taskId].status = TaskStatus.RUNTIME_ERROR
                failed_task = self._task_tracker[taskId]
                logger.error(
                    f"Task {failed_task.task_name} failed to run.\n{error_msg}"
                )
                pass
            case TaskRunResult.SKIPPED:
                self._task_tracker[taskId].status = TaskStatus.SKIPPED
