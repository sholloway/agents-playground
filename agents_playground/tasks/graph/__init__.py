from collections.abc import Sequence
from dataclasses import dataclass, field

from agents_playground.tasks.registry import TaskRegistry, global_task_registry
from agents_playground.tasks.resources import (
    TaskResourceRegistry,
    TaskResourceTracker,
    global_task_resource_registry,
)
from agents_playground.tasks.tracker import TaskTracker
from agents_playground.tasks.types import TaskDef, TaskLike, TaskName, TaskStatus


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

    def provision(self, name: TaskName, *args, **kwargs) -> TaskLike:
        """Provisions a task and adds it to the tracker.

        Args:
        - name: The name of the task to provision.
        - args: The positional arguments to pass to the TaskLike.
        - kwargs: The named arguments to pass to the TaskLike.

        Returns:
        The instance of the task that was provisioned.
        """
        task = self.task_registry.provision(name, *args, **kwargs)
        self.task_tracker.track(task)
        return task

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
        tasks_to_check: tuple[TaskLike, ...] = self.task_tracker.filter_by_status(status_filter)
        
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

            
    

    def is_valid(self) -> tuple[bool, str]:
        """
        Determines if the provisioned tasks and resources form a valid task graph that can be run.

        A valid task graph is one that:
        - Based on the inter-task relationships all tasks will eventually be able to run.

        Effects:
        -
        """
        ...
