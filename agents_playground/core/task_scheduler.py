from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import os
import select
import time
from typing import Any, Callable, Deque, Dict, List, Optional, Generator, Union, cast
from agents_playground.counter.counter import Counter, CounterBuilder

from agents_playground.core.polling_queue import PollingQueue
from agents_playground.sys.logger import get_default_logger
from agents_playground.sys.profile_tools import total_size

logger = get_default_logger()


def time_query() -> float:
    """Return the time in ms."""
    return time.process_time() * 1000


@dataclass
class TaskMetric:
    # Metrics
    registered_time: Union[int, float]
    started_time: Union[int, float] = field(init=False, default=-1)
    completed_time: Union[int, float] = field(init=False, default=-1)
    removed_time: Union[int, float] = field(init=False, default=-1)

    def complete(self) -> bool:
        return (
            self.registered_time != -1
            and self.started_time != -1
            and self.completed_time != -1
            and self.removed_time != -1
        )


TaskId = Union[int, float]
# Task = Callable[..., Generator]


def pending_task_counter() -> Counter:
    return CounterBuilder.count_up_from_zero()


@dataclass
class Task:
    task_id: TaskId
    parent_id: Optional[TaskId]
    task_ref: Callable  # Can be a pointer to a function or a generator that hasn't been initialized.
    args: List[Any]  # Positional parameters for the task.
    kwargs: Dict[str, Any]  # Named parameters for the task.
    # The number of tasks this task needs to complete before it can be run again.
    waiting_on_count: Counter = field(init=False, default_factory=pending_task_counter)
    initialized: bool = field(
        init=False, default=False
    )  # Indicates if task has been initialized.
    coroutine: Optional[Generator] = field(
        init=False, default=None
    )  # A coroutine that is suspended.

    def reduce_task_dependency(self) -> None:
        self.waiting_on_count.decrement()

    def read_to_run(self) -> bool:
        return self.waiting_on_count.at_min_value()


def do_nothing(*args, **kwargs) -> None:
    return


class EmptyPendingTask(Task):
    def __init__(self):
        super().__init__(-1, None, do_nothing, [], {})

    def reduce_task_dependency(self) -> None:
        self.waiting_on_count.decrement()

    def read_to_run(self) -> bool:
        return False


class TaskPriority(Enum):
    HIGH = 0
    NORMAL = 1
    LOW = 2


class ScheduleTraps(Enum):
    NEXT_FRAME = 0


class TaskScheduler:
    def __init__(self, profile: bool = False) -> None:
        """
        Args
          - profile: Enables collecting metrics on the scheduler.
        """
        self._registered_tasks_counter = CounterBuilder.count_up_from_zero()
        self._pending_tasks = CounterBuilder.count_up_from_zero()
        self._tasks_store: dict[Optional[TaskId], Task] = (
            dict()
        )  # Note: The Optional[TaskId] is in place because of the parent_id can be None.
        self._ready_to_initialize_queue: PollingQueue = PollingQueue(
            self._initialize_task
        )
        self._ready_to_resume_queue: PollingQueue = PollingQueue(self._resume_task)
        self._hold_for_next_frame: Deque[TaskId] = deque()
        self._stopped = False
        self._profile = profile
        self._metrics: dict[str, Any] = {
            "ready_to_initialize_queue_depth": [],  # Format: Tuple(frame: int, depth: int)
            "ready_to_resume_queue_depth": [],  # Format: Tuple(frame: int, depth: int)
            "registered_tasks": [],  # Format: Tuple(frame: int, tasks_count: int)
            "task_times": {},  # Format: {task_id: TaskId, TaskMetric}
            "sim_start_time": None,
            "sim_stop_time": None,
            "register_memory": [],  #  Memory used by self._tasks. Format: Tuple(frame: int, memory_size: float)
        }

    def __del__(self) -> None:
        logger.info("TaskScheduler is deleted.")

    def purge(self) -> None:
        """Removes all coroutines from the scheduler."""
        self._tasks_store.clear()
        self._ready_to_initialize_queue.clear()
        self._ready_to_initialize_queue = cast(PollingQueue, None)
        self._ready_to_resume_queue.clear()
        self._ready_to_resume_queue = cast(PollingQueue, None)
        self._hold_for_next_frame.clear()
        self._registered_tasks_counter.reset()
        self._pending_tasks.reset()

    def metrics(self) -> Dict:
        return self._metrics

    def add_task(
        self,
        task: Callable,
        args: List[Any] = [],
        kwargs: Dict[str, Any] = {},
        parent_id: Optional[TaskId] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> TaskId:
        """Register a task to be run with the scheduler.

        Args
          - task: A function or coroutine to run in the future.
          - args: Any positional parameters to pass to the task.
          - kwargs: Any named parameters to pass to the task.

        Functions and Generators are expected to be of the form:
        def my_task(*args, **kwargs)...

        Generators and Coroutines should follow this pattern:
        def simple_coroutine(*args, **kwargs) -> Generator:
          # Process inputs
          try:
            while True:
              # Do the work here.
              yield ScheduleTraps.NEXT_FRAME # yield to the next frame if the task should be repeated.
          except GeneratorExit:
            logger.info('Task: simple_coroutine - GeneratorExit')
          finally:
            logger.info('Task: simple_coroutine - Task Completed')
        """
        if self._stopped:
            logger.debug("TaskScheduler: Add Task called while scheduler stopped.")
            return -1
        else:
            task_id: Union[int, float] = self._registered_tasks_counter.increment()
            self._pending_tasks.increment()
            self._tasks_store[task_id] = Task(task_id, parent_id, task, args, kwargs)
            if self._profile:
                self._metrics["task_times"][task_id] = TaskMetric(time_query())

            # TODO: Perhaps the dependency counters should be proper counters and not just ints.
            # They should be capped to not go below 0.
            if parent_id in self._tasks_store:
                self._tasks_store[parent_id].waiting_on_count.increment()

            # TODO May eventually use the priority parameter here.
            # Is a different data structure required here? (e.g. Priority Queue)
            self._ready_to_initialize_queue.append(task_id)
            return task_id

    def consume(self):
        logger.info("TaskScheduler: Consume")
        logger.info(f"Tasks: {len(self._tasks_store)}")
        logger.info(f"Queue Depth: {len(self._ready_to_initialize_queue)}")
        frame: float = 0  # Just used for benchmarking.
        if self._profile:
            self._metrics["sim_start_time"] = time_query()
        try:
            while not self._stopped and self._pending_tasks.value() > 0:
                logger.debug(
                    f"TaskScheduler.consume(): Pending Tasks {self._pending_tasks.value()}"
                )
                can_read, _, _ = select.select(
                    [self._ready_to_initialize_queue, self._ready_to_resume_queue],
                    [],
                    [],
                )
                if self._profile:
                    frame = time_query()
                    self._metrics["ready_to_initialize_queue_depth"].append(
                        (frame, len(self._ready_to_initialize_queue))
                    )
                    self._metrics["ready_to_resume_queue_depth"].append(
                        (frame, len(self._ready_to_resume_queue))
                    )
                    self._metrics["registered_tasks"].append(
                        (frame, len(self._tasks_store))
                    )
                    self._metrics["register_memory"].append(
                        (frame, total_size(self._tasks_store))
                    )
                for q in can_read:
                    q.process_item()
            else:
                logger.info("TaskScheduler: Task Scheduler Stopped")
        except Exception as e:
            logger.exception(
                "TaskScheduler: Caught an exception in the consume function"
            )
            logger.exception(e)
            # If we're running the a pytest context, then re-raise the error to fail the test.
            if "PYTEST_CURRENT_TEST" in os.environ:
                raise e
        finally:
            logger.info("TaskScheduler: Done Consuming")
            if self._profile:
                self._metrics["sim_stop_time"] = time_query()

    def start(self) -> None:
        """Set a flag to allow scheduling tasks."""
        logger.info("TaskScheduler: Start Called")
        self._stopped = False

    def stop(self) -> None:
        """Set a flag to trigger a stop.
        The scheduler will stop accepting new tasks and stop once the running tasks
        are complete.
        """
        logger.info("TaskScheduler: Stop Called")
        self._stopped = True

    def remove_task(self, task_id: TaskId) -> None:
        logger.info(f"Attempting to remove task {task_id}")
        if task_id in self._tasks_store:
            finished_task: Task = self._tasks_store[task_id]
            if self._profile:
                self._metrics["task_times"][task_id].removed_time = time_query()
            # If the completed coroutine has a parent, decrement it's reference counter.
            self._remove_reference_to(finished_task.parent_id)
            del self._tasks_store[task_id]
            logger.info(f"TaskScheduler: Removed Task - {task_id}")

    def queue_holding_tasks(self) -> None:
        logger.info("TaskScheduler: Queue holding tasks for next cycle tick.")
        while len(self._hold_for_next_frame) > 0:
            task_id = self._hold_for_next_frame.pop()
            self._ready_to_resume_queue.append(task_id)
            self._pending_tasks.increment()

    def _remove_reference_to(self, task_id: Optional[TaskId]) -> None:
        """Remove a reference to a task.
        Decrements a task's reference counter. If the counter gets to zero, places
        it on appropriate queue.
        """
        task: Task = self._tasks_store.get(task_id, EmptyPendingTask())
        task.reduce_task_dependency()
        if task.read_to_run():
            self._queue_task_to_run(task)

    def _queue_task_to_run(self, task: Task) -> None:
        appropriate_queue = (
            self._ready_to_resume_queue
            if task.initialized
            else self._ready_to_initialize_queue
        )
        appropriate_queue.append(task.task_id)

    def _initialize_task(self, task_id: TaskId) -> None:
        logger.info(f"TaskScheduler: Starting Task {task_id}")
        pending_task: Task = self._tasks_store.get(task_id, EmptyPendingTask())
        if not pending_task.read_to_run() or isinstance(pending_task, EmptyPendingTask):
            # This task has other tasks that need to run first. Do nothing with it.
            return

        if self._profile:
            self._metrics["task_times"][task_id].started_time = time_query()

        self._pending_tasks.decrement()

        # Inject context related data for the task.
        task_context = {"task_id": task_id, "ts": self, **pending_task.kwargs}

        # Initialize the coroutine or run if it's a regular function.
        pending_task.initialized = True
        coroutine = pending_task.task_ref(*pending_task.args, **task_context)

        if hasattr(coroutine, "__next__"):
            # Dealing with a Coroutine or Generator Iterator.
            self._run_coroutine(pending_task, coroutine)
        else:
            # Dealing with a regular function.
            self._finalize_task_run(task_id)

    def _run_coroutine(self, pending_task, coroutine) -> None:
        try:
            instruction = next(coroutine)
            # Save a reference to the coroutine and queue it up to be resumed later.
            pending_task.coroutine = coroutine
            self._post_process_task(pending_task, instruction)
        except StopIteration:
            self._finalize_task_run(pending_task.task_id)

    def _resume_task(self, task_id: TaskId):
        # Note: Only coroutine/generator iterators can be resumed.
        logger.info(f"TaskScheduler: Resuming Task - {task_id}")
        pending_task: Task = self._tasks_store[task_id]
        self._pending_tasks.decrement()
        try:
            if pending_task.coroutine:
                instruction = pending_task.coroutine.send(None)
                self._post_process_task(pending_task, instruction)
        except StopIteration:
            self._finalize_task_run(task_id)

    def _post_process_task(self, ran_task: Task, instruction: ScheduleTraps) -> None:
        if instruction and instruction is ScheduleTraps.NEXT_FRAME:
            logger.info(
                f"TaskScheduler: Queuing Task {ran_task.task_id} for next frame."
            )
            self._hold_for_next_frame.append(ran_task.task_id)
        elif ran_task.read_to_run():
            self._pending_tasks.increment()
            self._ready_to_resume_queue.append(ran_task.task_id)

    def _finalize_task_run(self, task_id: TaskId) -> None:
        # This task is complete so remove it.
        if self._profile:
            self._metrics["task_times"][task_id].completed_time = time_query()
        self.remove_task(task_id)


"""
TODO
The _initialize_task is way too complicated. Some thoughts:
- The logic of handling regular functions and coroutines should be split out.
  hasattr(coroutine, '__next__') might all be extractable.
- The code that handles scheduling future work in both _initialize_task and _resume_task
  looks to be identical. This might be extractable.
- Can the conditional if instruction and instruction is ScheduleTraps.NEXT_FRAME 
  be expressed in a more readable way? Is this a better fit for Python 3.10 pattern matching?
- Can the profiling code and metrics collection code be handled by a decorator?
  This seems like a fit for some kind of wrapper.
"""
