from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Any, Callable, Generator, Generic, Protocol, Type, TypeVar

from agents_playground.counter.counter import Counter
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


class TaskStatus(IntEnum):
    INITIALIZED = auto()
    BLOCKED = auto()
    READY_FOR_ASSIGNMENT = auto()
    ASSIGNED = auto()
    RUNNING = auto()
    COMPLETE = auto()


class TaskResourceStatus(IntEnum):
    """
    Enumerated status for the life cycle of a task resource.
    """

    ALLOCATED = 1  # The resource has had it's memory allocated.
    RELEASED = 2  # The resource has had it's memory released.


class TaskRunResult(IntEnum):
    FAILED = 0
    SUCCESS = 1


class TaskLike(Protocol):
    """The contract for provisioned task."""

    task_name: TaskName  # The name that was used to provision the task.
    task_id: TaskId  # Unique Identifier of the task.

    # A pointer to a function to run.
    action: Callable[[list, dict], TaskRunResult]

    args: tuple[Any, ...]  # Positional parameters for the task's action function.
    kwargs: dict[str, Any]  # Named parameters for the task's action function.
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
        tasks: Sequence[TaskLike],
        notify: Callable[[TaskId, TaskRunResult, TaskErrorMsg], None],
    ) -> None: ...
