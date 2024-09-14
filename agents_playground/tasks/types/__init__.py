from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Any, Callable, Generator, Protocol, Type

from agents_playground.counter.counter import Counter
from agents_playground.fp import Maybe

type TaskId = int
type TaskName = str
type ResourceId = str
type ResourceType = str

class TaskStatus(IntEnum):
    INITIALIZED = auto()
    BLOCKED = auto()
    READY_FOR_ASSIGNMENT = auto()
    ASSIGNED = auto()
    RUNNING = auto()
    COMPLETE = auto()

class TaskLike(Protocol):
    """The contract for provisioned task."""
    task_id: TaskId         # Unique Identifier of the task.
    task_ref: Callable      # A pointer to a function or a generator that hasn't been initialized.
    args: list[Any]         # Positional parameters for the task.
    kwargs: dict[str, Any]  # Named parameters for the task.
    status: TaskStatus

    # required_before_tasks: list[TaskId]
    # inputs: dict[ResourceId, TaskResource]
    # outputs: dict[ResourceId, TaskResource]

    # The number of tasks this task needs to complete before it can be run again.
    waiting_on_count: Counter

    # Indicates if task has been initialized.
    initialized: bool

    # A coroutine that is suspended. This is used to store the coroutine that was originally
    # stored on self.task_ref
    coroutine: Maybe[Generator]

    def reduce_task_dependency(self) -> None:
        ...

    def read_to_run(self) -> bool:
        ...

@dataclass
class TaskDef:
    """
    A container class. Responsible for containing the metadata 
    required to provision a task instance.
    """
    name: TaskName
    type: Type # The type of task to provision.

    # The list of tasks that must run before this type of task.
    required_before_tasks: list[TaskName] = field(default_factory=list)

    # The list of required inputs that must be allocated for 
    # this type of task to run.
    inputs: list[ResourceId] = field(default_factory=list)

    # The list of outputs this task must produce.
    outputs: list[ResourceId] = field(default_factory=list)
