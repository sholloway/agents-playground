# Run With:
# poetry run python ./benchmarks/scheduler.py
# Debug With:
# PYTHONBREAKPOINT="pudb.set_trace" poetry run python -X dev ./benchmarks/scheduler.py

from __future__ import annotations

"""
The Goal
This files explores leveraging Python coroutines as a simple way to create 
hierarchical tasks. The intention is that this may be a good way to organize 
simulation code.

This shall be compared to using the asyncio module for doing the same thing.
"""

"""
Ongoing Notes
A task is a coroutine that can be paused with a yield statement.

It can be interacted with: https://docs.python.org/3.9/reference/expressions.html?highlight=yield#generator-expressions
- task() - Run the task until the first yield or completion.
- next(task) - Run the suspended task to the next yield or completion. 
- task.send(...) - Resumes the execution and “sends” a value into the generator function. 
- task.throw(...) - Raises an exception of type type at the point where the generator was paused, and returns the next value yielded by the generator function.
- task.close() - Raises a GeneratorExit at the point where the generator function was paused.

They can Throw Exceptions:
- StopIteration - https://docs.python.org/3.9/library/exceptions.html#StopIteration
- GeneratorExit - https://docs.python.org/3.9/library/exceptions.html#GeneratorExit

Example
def task(value = None):
  try:
    while True:
      # Value will be set to the value passed in by send(...).
      value = yield f'Hello {value}'
  finally:
    print('This is ran when task.close() is called.')

Reference Counting
The gist of referencing counting is that every item has an associated counter.
This counter tracks how many things refer to that item. When the counter 
is 0 there are no other items that need the item to exist. 

If a task spawns a blocking subtask, then by passing in the parent's task_id to 
add_tasks a reference counter will prevent the parent task from running again 
until the child tasks have completed. Non-blocking tasks simply don't reference
the parent task's id.

BUGs
- None

TODOs
- Add priorities. High priority should go to the front of the line.
- Finish this little experiment.
- Add benchmarking measurements to this. 
  - Measure the upper limit on the number of coroutines that can be processed like this.
  - Things to track:
    - Queue Depth for each queue
      At what point does the queue depth become unable to be completed in a frame (16.67 ms)? 
    - # Registered Tasks
    - Memory Utilization
- Create a second benchmark file. 
  - Try doing basically the same thing but using the asynco module.
  - Try defining tasks with the async keyword.
  - Evaluate asyncio.create_task and asynco.gather
"""


from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import itertools
from typing import Any, Callable, Dict, Generator, List, Optional, Union
import socket
import select
import threading
import time
import logging

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

class SelfPollingQueue(deque):
  def __init__(self, item_processor: Callable) -> None:
    super().__init__()
    self._put_socket, self._get_socket = socket.socketpair()
    self._item_processor: Callable = item_processor

  def fileno(self):
    return self._get_socket.fileno()

  def append(self, item: Any) -> None:
    super().append(item)
    self._put_socket.send(b'x')
    
  def popleft(self) -> Any:
    self._get_socket.recv(1)
    return super().popleft()

  def process_item(self) -> None:
    item = self.popleft()
    self._item_processor(item)

class TaskPriority(Enum):
  HIGH = 0
  NORMAL = 1
  LOW = 2

class TaskScheduler:
  def __init__(self) -> None:
    self._task_counter = itertools.count()
    self._tasks: dict[TaskId, PendingTask] = dict()
    self._ready_to_initialize_queue: SelfPollingQueue = SelfPollingQueue(self._initialize_task)
    self._ready_to_resume_queue: SelfPollingQueue = SelfPollingQueue(self._resume_task)

  def _initialize_task(self, task_id: TaskId) -> None:
    logging.info(f'Starting Task: {task_id}')
    pending_task: PendingTask = self._tasks[task_id]      

    # Inject context related data for the task.
    task_context = {'task_id': task_id, 'ts': self, **pending_task.kwargs}

    # Initialize the coroutine or run if it's a regular function.
    coroutine = pending_task.task_ref(*pending_task.args, **task_context)

    if hasattr(coroutine, '__next__'): #Dealing with a Coroutine or Generator Iterator.
      try:
        next(coroutine)
        # Save a reference to the coroutine and queue it up to be resumed later.
        pending_task.coroutine = coroutine
        if pending_task.waiting_on_count <= 0:
          self._ready_to_resume_queue.append(task_id)
      except StopIteration:
        # This task is complete so remove it from the task registry.
        self.remove_task(task_id)
    else: 
      # Dealing with a regular function. 
      # It's done so just remove it from the task registry.
      self.remove_task(task_id)

  def _resume_task(self, task_id: TaskId):
    # Note: Only coroutine/generator iterators can be resumed.
    logging.info(f'Resuming Task: {task_id}')
    pending_task: PendingTask = self._tasks[task_id]    
    try: 
      next(pending_task.coroutine)
      if pending_task.waiting_on_count <= 0:
        self._ready_to_resume_queue.append(task_id)
    except StopIteration:
      # This task is complete so remove it. 
      self.remove_task(task_id)

  def consume(self):
    logging.info('In Consume')
    logging.info(f'Tasks: {len(self._tasks)}')
    logging.info(f'Queue Depth: {len(self._ready_to_initialize_queue)}')
    try:
      while True:
        can_read, _, _ = select.select([self._ready_to_initialize_queue, self._ready_to_resume_queue], [], [])
        for q in can_read:
          q.process_item()
    except Exception as e:
      logging.exception('Caught an exception in the consume function')

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
    task_id = next(self._task_counter)
    self._tasks[task_id] = PendingTask(task_id, parent_id, 0, task, args, kwargs)
    if parent_id in self._tasks:
      self._tasks[parent_id].waiting_on_count += 1

    # TODO May eventually use the priority parameter here.
    # Is a different data structure required here? (e.g. Priority Queue)
    self._ready_to_initialize_queue.append(task_id)
    return task_id

  def remove_task(self, task_id: TaskId) -> None: 
    logging.info(f'Attempting to remove task {task_id}')
    if task_id in self._tasks:
      finished_task = self._tasks[task_id]
      # If the completed coroutine has a parent, decrement it's reference counter.
      self._remove_reference(finished_task.parent_id)
      del self._tasks[task_id]
      logging.info(f'Removed Task: {task_id}')

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

def count_down(name: str, count = 5, *args, **kargs) -> None:
  try:
    while count > 0:
      logging.info(f'{name} Count Down: {count}')
      count -= 1
      yield
  finally:
    logging.info(f'{name} finalized')

def regular_function(*args, **kargs) -> None:
  logging.info('Regular function. No yield expression.')

def uc_rerunning(ts: TaskScheduler):
  """Use case: Keep re-running a paused task if the coroutine allows it."""
  ts.add_task(count_down, ('A', 10))
  ts.add_task(count_down, ('B', 5))
  ts.add_task(regular_function)
  ts.add_task(count_down, ('C', 22))
  ts.add_task(count_down, ('D', 15))
   
def call_four_coroutines(*args, **kwargs):
  """
  Args
    - name: The name of this coroutine to use for logging.
    - task_context: The TaskContext object injected by the TaskScheduler
  """
  # This hacky monster finds the item in scope (felf == self)
  # felf = globals()[sys._getframe().f_code.co_name]
  # print(felf)
  # print(dir(felf))
  # context: TaskContext = felf.context

  logging.info('Starting call_four_coroutines')
  logging.debug(f'Args: {args}')
  logging.debug(f'KWArgs: {kwargs}')
  name = kwargs['name']
  task_id = kwargs['task_id']
  ts = kwargs['ts']

  try:
    ts.add_task(count_down, ['A', 10], parent_id=task_id)
    ts.add_task(count_down, ['B', 5], parent_id=task_id)
    ts.add_task(regular_function, parent_id=task_id)
    yield
  finally:
    logging.info(f'{name} finalized')

def uc_hierarchy(ts: TaskScheduler):
  """Use Case: A coroutine adds other coroutines that must be completed before it itself can be processed again."""
  ts.add_task(call_four_coroutines, [], { 'name': 'call_four_coroutines'})

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')
  ts = TaskScheduler()

  schedule_thread = threading.Thread(
    name="schedule_thread", 
    target=ts.consume, 
    args=(), 
    daemon=True
  )
  schedule_thread.start()

  uc_rerunning(ts)
  uc_hierarchy(ts)

  time.sleep(1)
  logging.info(f'Exiting the app.')
  logging.info(f'Tasks: {len(ts._tasks)}')