from dataclasses import dataclass, field
from typing import Any, Callable, Generator

from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp import Maybe, Nothing
from agents_playground.tasks.types import TaskId, TaskName, TaskStatus


def pending_task_counter() -> Counter:
    return CounterBuilder.count_up_from_zero()


def init_nothing() -> Maybe:
    return Nothing()


@dataclass(init=False)
class GenericTask:
    args: tuple[Any, ...]  # Positional parameters for the task.
    kwargs: dict[str, Any]  # Named parameters for the task.
    action: Callable
    task_name: TaskName
    task_id: TaskId
    status: TaskStatus
