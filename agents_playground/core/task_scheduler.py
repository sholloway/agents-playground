
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import select
import time
from typing import Any, Callable, Dict, List, Optional, Generator, Union

from agents_playground.core.polling_queue import PollingQueue
from agents_playground.sys.logger import get_default_logger
from agents_playground.sys.profile_tools import total_size

logger = get_default_logger()

def time_query() -> int:
  """Return the time in ms."""
  return time.process_time() * 1000

@dataclass
class TaskMetric:
  # Metrics
  registered_time: int
  started_time: int = field(init=False, default=-1)
  completed_time: int = field(init=False, default=-1)
  removed_time: int = field(init=False, default=-1)

  def complete(self) -> bool:
    return self.registered_time != -1 and \
      self.started_time != -1 and \
      self.completed_time != -1 and \
      self.removed_time != -1

class Counter:
  def __init__(self, 
    start: Union[int, float]=0, 
    increment_step: Union[int, float]=1, 
    decrement_step: Union[int, float]=1
  ):
    self._start = start
    self._value: Union[int, float] = start
    self._increment_step: Union[int, float] = increment_step
    self._decrement_step: Union[int, float] = decrement_step

  def increment(self) -> Union[int, float]:
    self._value += self._increment_step
    return self._value

  def decrement(self) -> Union[int, float]:
    self._value -= self._decrement_step
    return self._value

  def value(self) -> Union[int, float]:
    return self._value

  def reset(self):
    self._value = self._start

TaskId = int
TaskRefCounter = int
Task = Callable[..., None]

@dataclass
class PendingTask:
  task_id: TaskId
  parent_id: TaskId
  # The number of tasks this task needs to complete before it can be run again.
  waiting_on_count: TaskRefCounter 
  task_ref: Task # This is either a pointer to a function or a generator that hasn't been initialized.
  args: List[Any] # Positional parameters for the task.
  kwargs: Dict[str, Any] # Named parameters for the task.
  coroutine: Optional[Generator] = field(init=False) # A coroutine that is suspended.

class TaskPriority(Enum):
  HIGH = 0
  NORMAL = 1
  LOW = 2

class ScheduleTraps(Enum):
  NEXT_FRAME = 0

class TaskScheduler:
  def __init__(self, profile: bool=False) -> None:
    """
    Args
      - profile: Enables collecting metrics on the scheduler.
    """
    self._task_counter = Counter(start=0)
    self._pending_tasks = Counter(start=0)
    self._tasks: dict[TaskId, PendingTask] = dict()
    self._ready_to_initialize_queue: PollingQueue = PollingQueue(self._initialize_task)
    self._ready_to_resume_queue: PollingQueue = PollingQueue(self._resume_task)
    self._hold_for_next_frame: List[TaskId] = deque()
    self._stopped = False
    self._profile = profile
    self._metrics = {
      'ready_to_initialize_queue_depth': [], # Format: Tuple(frame: int, depth: int)
      'ready_to_resume_queue_depth': [], # Format: Tuple(frame: int, depth: int)
      'registered_tasks': [], # Format: Tuple(frame: int, tasks_count: int)
      'task_times': {}, # Format: {task_id: TaskId, TaskMetric}
      'sim_start_time': None,
      'sim_stop_time': None,
      'register_memory': [] #  Memory used by self._tasks. Format: Tuple(frame: int, memory_size: float)
    }

  def metrics(self) -> Dict:
    return self._metrics

  def _initialize_task(self, task_id: TaskId) -> None:
    logger.info(f'TaskScheduler: Starting Task {task_id}')
    if self._profile:
      self._metrics['task_times'][task_id].started_time = time_query()
    self._pending_tasks.decrement()
    pending_task: PendingTask = self._tasks[task_id]      

    # Inject context related data for the task.
    task_context = {'task_id': task_id, 'ts': self, **pending_task.kwargs}

    # Initialize the coroutine or run if it's a regular function.
    coroutine = pending_task.task_ref(*pending_task.args, **task_context)

    if hasattr(coroutine, '__next__'): #Dealing with a Coroutine or Generator Iterator.
      try:
        # TODO: Rename. What does the David M's system call the response?
        instruction = next(coroutine)
        # Save a reference to the coroutine and queue it up to be resumed later.
        pending_task.coroutine = coroutine
        if instruction and instruction is ScheduleTraps.NEXT_FRAME:
          logger.info(f'TaskScheduler: Queuing Task {task_id} for next frame.')
          self._hold_for_next_frame.append(task_id)
        elif pending_task.waiting_on_count <= 0:
          self._pending_tasks.increment()
          self._ready_to_resume_queue.append(task_id)
      except StopIteration:
        # This task is complete so remove it from the task registry.
        if self._profile:
          self._metrics['task_times'][task_id].completed_time = time_query()
        self.remove_task(task_id)
    else: 
      # Dealing with a regular function. 
      # It's done so just remove it from the task registry.
      if self._profile:
        self._metrics['task_times'][task_id].completed_time = time_query()
      self.remove_task(task_id)

  def _resume_task(self, task_id: TaskId):
    # Note: Only coroutine/generator iterators can be resumed.
    logger.info(f'TaskScheduler: Resuming Task - {task_id}')
    pending_task: PendingTask = self._tasks[task_id]  
    self._pending_tasks.decrement()  
    try: 
      instruction = pending_task.coroutine.send(None) #Todo: Pass frame data
      if instruction and instruction is ScheduleTraps.NEXT_FRAME:
        logger.info(f'TaskScheduler: Queuing Resumed Task {task_id} for next frame.')
        self._hold_for_next_frame.append(task_id)
      elif pending_task.waiting_on_count <= 0:
        self._pending_tasks.increment()
        self._ready_to_resume_queue.append(task_id)
    except StopIteration:
      # This task is complete so remove it. 
      if self._profile:
        self._metrics['task_times'][task_id].completed_time = time_query()
      self.remove_task(task_id)

  def stop(self):
    '''Set a flag to trigger a stop.
    The scheduler will stop accepting new tasks and stop once the running tasks 
    are complete.
    '''
    logger.info('TaskScheduler: Stop Called')
    self._stopped = True
    
  def consume(self):
    logger.info('TaskScheduler: Consume')
    logger.info(f'Tasks: {len(self._tasks)}')
    logger.info(f'Queue Depth: {len(self._ready_to_initialize_queue)}')
    frame = 0 # Just used for benchmarking.
    if self._profile:
      self._metrics['sim_start_time'] = time_query()
    try:
      while not self._stopped and self._pending_tasks.value() > 0:
        logger.debug(f'TaskScheduler.consume(): Pending Tasks {self._pending_tasks.value()}')
        can_read, _, _ = select.select([self._ready_to_initialize_queue, self._ready_to_resume_queue], [], [])
        if self._profile:
          frame = time_query()
          self._metrics['ready_to_initialize_queue_depth'].append((frame, len(self._ready_to_initialize_queue)))
          self._metrics['ready_to_resume_queue_depth'].append((frame, len(self._ready_to_resume_queue)))
          self._metrics['registered_tasks'].append((frame, len(self._tasks)))
          self._metrics['register_memory'].append((frame, total_size(self._tasks)))
        for q in can_read:
          q.process_item()
      else:
        logger.info('TaskScheduler: Task Scheduler Stopped')
    except Exception as e:
      logger.exception('TaskScheduler: Caught an exception in the consume function')
    finally:
      logger.info('TaskScheduler: Done Consuming')
      if self._profile:
        self._metrics['sim_stop_time'] = time_query()

  def add_task(self, 
    task: Union[Callable, Generator], 
    args: List[Any] = [],
    kwargs: Dict[str, Any] = {},
    parent_id: Optional[TaskId] = None, 
    priority: TaskPriority = TaskPriority.NORMAL) -> TaskId:
    """Register a task to be run with the scheduler.

    Args
      - task: A function or coroutine to run in the future.
      - args: Any positional parameters to pass to the task.
      - kwargs: Any named parameters to pass to the task.
    """
    if self._stopped:
      logger.debug('TaskScheduler: Add Task called while scheduler stopped.')
      return -1
    else:
      task_id = self._task_counter.increment()
      self._pending_tasks.increment()
      self._tasks[task_id] = PendingTask(task_id, parent_id, 0, task, args, kwargs)
      if self._profile:
        self._metrics['task_times'][task_id] = TaskMetric(time_query())

      if parent_id in self._tasks:
        self._tasks[parent_id].waiting_on_count += 1

      # TODO May eventually use the priority parameter here.
      # Is a different data structure required here? (e.g. Priority Queue)
      self._ready_to_initialize_queue.append(task_id)
      return task_id

  def remove_task(self, task_id: TaskId) -> None: 
    logger.info(f'Attempting to remove task {task_id}')
    if task_id in self._tasks:
      finished_task: PendingTask = self._tasks[task_id]
      if self._profile:
        self._metrics['task_times'][task_id].removed_time = time_query()
      # If the completed coroutine has a parent, decrement it's reference counter.
      self._remove_reference(finished_task.parent_id)
      del self._tasks[task_id]
      logger.info(f'TaskScheduler: Removed Task - {task_id}')

  def _remove_reference(self, task_id: TaskId) -> None:
    """ Remove a reference to a task.
    Decrements a task's reference counter. If the counter gets to zero, places 
    it on the ready to resume queue.
    """
    if task_id in self._tasks:
      task = self._tasks[task_id]
      task.waiting_on_count -= 1
      if task.waiting_on_count <= 0:
        self._ready_to_resume_queue.append(task_id)

  def queue_holding_tasks(self) -> None:
    logger.info('TaskScheduler: Queue holding tasks for next cycle tick.')
    while len(self._hold_for_next_frame) > 0:
      task_id = self._hold_for_next_frame.pop()
      self._ready_to_resume_queue.append(task_id)
      self._pending_tasks.increment()