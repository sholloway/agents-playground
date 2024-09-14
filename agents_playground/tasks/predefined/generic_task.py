from dataclasses import dataclass, field
from typing import Any, Callable, Generator

from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp import Maybe, Nothing
from agents_playground.tasks.types import TaskId, TaskName, TaskStatus

def pending_task_counter() -> Counter:
    return CounterBuilder.count_up_from_zero()

def init_nothing() -> Maybe:
    return Nothing()

@dataclass(init=True)
class GenericTask:
    task_ref: Callable      # A pointer to a function or a generator that hasn't been initialized.
    args: list[Any]         # Positional parameters for the task.
    kwargs: dict[str, Any]  # Named parameters for the task.
    task_name: TaskName = field(init=False)
    task_id: TaskId = field(init=False)
    status: TaskStatus = field(default=TaskStatus.INITIALIZED)

    # The number of tasks this task needs to complete before it can be run again.
    waiting_on_count: Counter = field(default_factory=pending_task_counter)

    # Indicates if task has been initialized.
    initialized: bool = field(default=False)  

    # A coroutine that is suspended. This is used to store the coroutine that was originally
    # stored on self.task_ref
    coroutine: Maybe[Generator] = field(default_factory=init_nothing)  

    def reduce_task_dependency(self) -> None:
        self.waiting_on_count.decrement()

    def read_to_run(self) -> bool:
        return self.waiting_on_count.at_min_value()