from dataclasses import dataclass, field
import sys
from typing import Any, Callable, Generator

from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp import Maybe, Nothing
from agents_playground.sys.profile_tools import total_size
from agents_playground.tasks.types import (
    ResourceSeq,
    TaskId,
    TaskName,
    TaskSeq,
    TaskStatus,
)


def pending_task_counter() -> Counter:
    return CounterBuilder.count_up_from_zero()


def init_nothing() -> Maybe:
    return Nothing()


@dataclass()
class GenericTask:
    """
    Implements TaskLike
    """

    # Positional parameters for the task.
    # args: tuple[Any, ...] = field(init=False)

    # Named parameters for the task.
    # kwargs: dict[str, Any] = field(init=False)

    action: Callable = field(init=False)
    name: TaskName = field(init=False)
    id: TaskId = field(init=False)
    status: TaskStatus = field(init=False)
    waiting_on: dict[str, TaskSeq | ResourceSeq] = field(
        default_factory=dict, init=True
    )

    def __sizeof__(self) -> int:
        base_size: int = sys.getsizeof(super())
        return base_size + total_size(self.__dict__)
