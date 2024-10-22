from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum, IntEnum, StrEnum, auto
from typing import Any, Callable, Generic, Iterator, NamedTuple, Protocol, Type, TypeVar

from agents_playground.containers.attr_dict import AttrDict
from agents_playground.containers.types import (
    MultiIndexedContainerLike,
    TaggableContainerLike,
)
from agents_playground.core.types import Bytes, TimeInNS
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


type TaskInputs = AttrDict
type TaskOutputs = AttrDict


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
    id: ResourceId
    name: ResourceName
    resource_status: TaskResourceStatus
    resource: Maybe[T] = field(default_factory=lambda: Nothing())


class ResourceAllocation(NamedTuple):
    id: ResourceId
    name: ResourceName
    size: Bytes

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
class SimulationTasks:
    initial_tasks: Sequence[TaskName]
    per_frame_tasks: Sequence[TaskName]
    render_tasks: Sequence[TaskName]
    shutdown_tasks: Sequence[TaskName]


class SimulationPhase(StrEnum):
    """
    Defines the various phases of a TaskGraph based simulation.
    """

    BEFORE_INITIALIZATION = auto()
    ON_INITIALIZATION = auto()
    AFTER_INITIALIZATION = auto()
    BEFORE_FRAME = auto()
    END_OF_FRAME = auto()
    ON_SHUTDOWN = auto()


@dataclass
class TaskResourceDef:
    """
    A container class. Responsible for containing the metadata
    required to provision a task resource instance.
    """

    name: ResourceName  # The unique name of the resource.
    type: ResourceType  # The type of resource to provision.
    # When the resource will be released.
    release_on: SimulationPhase | None = None


@dataclass
class TaskRunStep:
    id: TaskId
    name: TaskName
    started: TimeInNS
    finished: TimeInNS
    status: TaskStatus
    produced: tuple[ResourceName,...]


@dataclass
class TaskRunHistory:
    steps: tuple[TaskRunStep, ...]
    started: TimeInNS
    finished: TimeInNS


class TaskRunnerLike(Protocol):
    def run(
        self,
        task_graph: TaskGraphLike,
        tasks: Sequence[TaskLike],
        notify: Callable[[TaskId, TaskRunResult, TaskErrorMsg], None],
    ) -> TaskRunHistory: ...


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


class TaskResourceTrackerLike(
    MultiIndexedContainerLike, TaggableContainerLike, Protocol
):
    """
    Contract for a Task focused resource tracker.
    """


class TaskGraphLike(Protocol):
    def provision_task(self, name: TaskName) -> None:
        """Provisions a task and adds it to the tracker.

        Args:
        - name: The name of the task to provision.
        """
        ...

    def provision_tasks(self, task_names: Sequence[TaskName]) -> None:
        """Provision a sequence of tasks."""

    def provision_resource(
        self,
        name: ResourceName,
        instance: Any | None = None,
        release_on: SimulationPhase | None = None,
        *args,
        **kwargs,
    ) -> TaskResource: ...

    def provision_resources(self, resources: AttrDict) -> None:
        """
        Given a collection of resources, provision them in the
        resource tracker with the provided instances.

        Args:
            - name: The name of the resource to provision.
            - instance (optional): An instance of the resource to track. If none is provided then the task graph will attempt to provision an instance.
            - release_on (optional): The simulation phase to release the resource. Overrides the on_release specified on the ResourceDef.
            - args (optional): Positional parameters used to provision the resource instance. Ignored if instance is provided.
            - kwargs (optional): Named parameters used to provision the resource instance. Ignored if instance is provided.
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

    def resource_allocations(self) -> tuple[ResourceAllocation,...]:
        """
        Returns a collection of allocations.
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

    def run_all_ready_tasks(self) -> TaskRunHistory:
        """Run all tasks that have their status set to READY_FOR_ASSIGNMENT."""
        ...

    def run_until_done(self, verify_all_ran: bool = True) -> tuple[TaskRunHistory, ...]:
        """
        Continue to run tasks until they're all complete or the graph is blocked.

        Args:
            - verify_all_ran: If true, then check if all the tasks ran.

        Effects:
        - Calls check_if_blocked_tasks_are_ready to prompt tasks into ready status.
        - Runs tasks and pushes them into completed status.
        """
        ...

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

    def release_resources(self, phase: SimulationPhase) -> None:
        """
        Remove resources from the resource tracker.

        Args:
        - phase: The simulation phase used to identify the resources ready to be released.
        """
