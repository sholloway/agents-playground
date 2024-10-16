from __future__ import annotations

from collections import UserDict
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import Any, Callable, Generic, Iterator, Protocol, Type, TypeVar

from agents_playground.fp import Maybe, Nothing

type TaskId = int
type TaskName = str
type ResourceIndex = int
type ResourceId = int
type ResourceName = str
type ResourceType = Type
type ResourceTag = str
type TaskErrorMsg = str

type TaskSeq = Sequence[TaskName]
type ResourceSeq = Sequence[ResourceName]


class TaskStatus(Enum):
    INITIALIZED = auto()
    BLOCKED = auto()
    READY_FOR_ASSIGNMENT = auto()
    ASSIGNED = auto()
    RUNNING = auto()
    COMPLETE = auto()
    SKIPPED = auto()
    RUNTIME_ERROR = auto()


class TaskResourceStatus(IntEnum):
    """
    Enumerated status for the life cycle of a task resource.
    """

    ALLOCATED = 1  # The resource has had it's memory allocated.
    RELEASED = 2  # The resource has had it's memory released.


class TaskRunResult(IntEnum):
    FAILED = 0
    SUCCESS = 1
    SKIPPED = 2


class ResourceDict(UserDict):
    """
    Used for passing resources around.

    Behaves like a Python dict but enables setting attributes
    using dot notation.

    Note that the UserDict stores values in the data attribute
    with is an actual dict instance.
    """

    def __getitem__(self, key: ResourceName) -> Any:
        """
        Enables fetching attributes dictionary style.
        """
        return self.data[key]

    def __getattr__(self, key: ResourceName) -> Any:
        """
        Enables fetching attributes via dot notation.
        """
        return self.__getitem__(key)

    def __setattr__(self, key: ResourceName, value: Any):
        """
        Enables setting attributes via dot notation.
        """
        if key == "data":
            # Prevent overwriting the data attribute that stores
            # the class attributes.
            return super().__setattr__(key, value)
        return self.__setitem__(key, value)


type TaskInputs = ResourceDict
type TaskOutputs = ResourceDict


class TaskLike(Protocol):
    """The contract for provisioned task."""

    name: TaskName  # The name that was used to provision the task.
    id: TaskId  # Unique Identifier of the task.

    # A pointer to a function to run.
    action: Callable[[TaskGraphLike, TaskInputs, TaskOutputs], None]

    # args: tuple[Any, ...]  # Positional parameters for the task's action function.
    # kwargs: dict[str, Any]  # Named parameters for the task's action function.
    status: TaskStatus
    waiting_on: dict[str, TaskSeq | ResourceSeq]


T = TypeVar("T")


@dataclass
class TaskResource(Generic[T]):
    resource_id: ResourceId
    resource_name: ResourceName
    resource_status: TaskResourceStatus
    resource: Maybe[T] = field(default_factory=lambda: Nothing())


@dataclass
class TaskDef:
    """
    A container class. Responsible for containing the metadata
    required to provision a task instance.
    """

    name: TaskName
    type: Type  # The type of task to provision.
    action: Callable  # The function to run when the task is processed.

    # Only run the task if this evaluates to True
    run_if: Callable[[], bool] = field(default=lambda: True)

    # Indicate if the task must be run in the main thread.
    pin_to_main_thread: bool = False

    # The list of tasks that must run before this type of task.
    required_before_tasks: list[TaskName] = field(default_factory=list)

    # The list of required inputs that must be allocated for
    # this type of task to run.
    inputs: list[ResourceName] = field(default_factory=list)

    # The list of outputs this task must produce.
    outputs: list[ResourceName] = field(default_factory=list)


@dataclass
class TaskResourceDef:
    """
    A container class. Responsible for containing the metadata
    required to provision a task resource instance.
    """

    name: ResourceName
    type: ResourceType  # The type of resource to provision.


@dataclass
class SimulationTasks:
    initial_tasks: Sequence[TaskName]
    per_frame_tasks: Sequence[TaskName]
    render_tasks: Sequence[TaskName]
    shutdown_tasks: Sequence[TaskName]


class TaskRunnerLike(Protocol):
    def run(
        self,
        task_graph: TaskGraphLike,
        tasks: Sequence[TaskLike],
        notify: Callable[[TaskId, TaskRunResult, TaskErrorMsg], None],
    ) -> None: ...


class TaskRegistryLike(Protocol):
    def register(self, alias: str, task_def: TaskDef) -> None: ...
    def task_names(self) -> tuple[TaskName, ...]: ...
    def clear(self) -> None: ...
    def provision(self, alias: str) -> TaskLike: ...
    def __iter__(self) -> Iterator: ...
    def add_requirement(
        self, before_tasks: tuple[TaskName, ...], later_tasks: tuple[TaskName, ...]
    ) -> None: ...

    @property
    def provisioned_tasks_count(self) -> int: ...

    def __setitem__(self, key: str, value: TaskDef) -> None: ...
    def __getitem__(self, key: TaskName) -> TaskDef: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: str) -> bool: ...


class TaskResourceRegistryLike(Protocol):
    def register(self, alias: str, resource_def: TaskResourceDef) -> None: ...
    def provision(
        self, alias: str, instance: Any | None = None, *args, **kwargs
    ) -> TaskResource: ...
    def clear(self) -> None: ...
    def get(self, key: ResourceName) -> Maybe[TaskResourceDef]:
        """
        Similar to resource_registry["my_resource"] but returns the result
        wrapped in a Maybe. If the resource is not tracked then returns
        a Nothing instance.
        """
        ...

    def __setitem__(self, key: str, value: TaskResourceDef) -> None: ...
    def __getitem__(self, key: str) -> TaskResourceDef: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: str) -> bool: ...


class TaskTrackerLike(Protocol):
    def clear(self) -> None: ...
    def track(self, task: TaskLike | Sequence[TaskLike]) -> None: ...
    def release(self, task_ids: Sequence[TaskId]) -> int: ...
    def filter_by_status(
        self, filter: Sequence[TaskStatus], inclusive: bool = True
    ) -> tuple[TaskLike, ...]: ...
    def filter_by_name(self, filter: Sequence[TaskName]) -> tuple[TaskLike, ...]: ...
    def collect_by_name(self, filter: Sequence[TaskName]) -> tuple[TaskLike, ...]: ...
    def __getitem__(self, key: TaskId | TaskName) -> TaskLike: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: TaskId) -> bool: ...
    def __iter__(self) -> Iterator: ...


class TaskResourceTrackerLike(Protocol):
    def clear(self) -> None: ...
    def track(self, resource: TaskResource) -> ResourceId: ...
    def tag(self, name: ResourceName, tag: ResourceTag) -> None: ...
    def remove_tag(self, name: ResourceName, tag: ResourceTag) -> None: ...
    def delete_tag(self, tag: str) -> None: ...
    def filter(self, *tags: str) -> list[TaskResource]: ...
    def __getitem__(self, key: ResourceId | ResourceName) -> TaskResource: ...
    def get(self, key: ResourceId | ResourceName) -> Maybe[TaskResource]: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: ResourceId | ResourceName) -> bool: ...


class TaskGraphLike(Protocol):
    # task_registry: TaskRegistryLike
    # resource_registry: TaskResourceRegistryLike
    # task_tracker: TaskTrackerLike
    # resource_tracker: TaskResourceTrackerLike
    # task_runner: TaskRunnerLike

    def provision_task(self, name: TaskName) -> TaskLike:
        """Provisions a task and adds it to the tracker.

        Args:
        - name: The name of the task to provision.

        Returns:
        The instance of the task that was provisioned.
        """
        ...

    def provision_tasks(self, task_names: Sequence[TaskName]) -> None:
        """Provision a sequence of tasks."""

    def provision_resource(
        self, name: ResourceName, instance: Any | None = None, *args, **kwargs
    ) -> TaskResource: ...

    def provision_resources(self, resources: ResourceDict) -> None:
        """
        Given a collection of resources, provision them in the
        resource tracker with the provided instances.
        """

    def resource_def(self, key: ResourceName) -> Maybe[TaskResourceDef]:
        """
        Find a resource's registered definition by its name.
        Returns an instance of Nothing if a definition isn't found.
        """
        ...

    def resource(self, key: ResourceId | ResourceName) -> Maybe[TaskResource]:
        """
        Get a tracked, provisioned resource. If the resource isn't tracked then
        an instance of Nothing is returned.
        """
        ...

    def unwrap_tracked_resource(self, key: ResourceId | ResourceName) -> Any: ...

    def clear(self) -> None:
        """
        Deletes all provisioned resources and tasks and removes all registrations.
        Basically, resets the task graph to be empty.
        """

    def task_def(self, key: TaskName) -> TaskDef:
        """
        Find a task definition by its name.
        """
        ...

    def task(self, key: TaskId | TaskName) -> TaskLike:
        """
        Find a provisioned task by its ID or name.
        """
        ...

    def tasks_with_status(
        self, filter: Sequence[TaskStatus]
    ) -> tuple[TaskLike, ...]: ...

    def tasks_without_status(
        self, filter: Sequence[TaskStatus]
    ) -> tuple[TaskLike, ...]: ...

    def check_if_blocked_tasks_are_ready(self) -> None:
        """
        Inspect all provisioned tasks with a status of INITIALIZED or BLOCKED to see if
        they're ready to run. If they are, then update the status to READY_FOR_ASSIGNMENT.

        Effects:
        - Tasks that are INITIALIZED but blocked have their status set to BLOCKED.
        - Tasks that are INITIALIZED or BLOCKED have their status set to READY_FOR_ASSIGNMENT.
        """

    def run_all_ready_tasks(self) -> None:
        """Run all tasks that have their status set to READY_FOR_ASSIGNMENT."""

    def run_until_done(self, verify_all_ran: bool = True) -> None:
        """
        Continue to run tasks until they're all complete or the graph is blocked.

        Args:
            - verify_all_ran: If true, then check if all the tasks ran.

        Effects:
        - Calls check_if_blocked_tasks_are_ready to prompt tasks into ready status.
        - Runs tasks and pushes them into completed status.
        """

    def collect_inputs_for(self, task_name: TaskName) -> TaskInputs:
        """
        Collects all of the provisioned input resources for a task.
        """
        ...

    def release_completed_tasks(self) -> None:
        """
        Remove completed tasks from the task registry.
        """
        ...
