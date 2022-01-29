# Run With:
# poetry run python ./benchmarks/scheduler.py
# Debug With:
# PYTHONBREAKPOINT="pudb.set_trace" poetry run python -X dev ./benchmarks/scheduler.py

from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import itertools
from telnetlib import TSPEED
from typing import Any, Callable, Dict, Generator, List, Optional, Union
import socket
import select
import threading
import time
import sys
import logging

TaskId = int
TaskRefCounter = int
Task = Callable[..., None]

"""
A task is a coroutine that can be paused with a yield statement.

It can be interacted with: https://docs.python.org/3.9/reference/expressions.html?highlight=yield#generator-expressions
- task() - Run the task until the first yield or completion.
- next(task) - Run the suspended task to the next yield or completion. 
- task.send(...) - Resumes the execution and “sends” a value into the generator function. 
- task.throw(...) - Raises an exception of type type at the point where the generator was paused, and returns the next value yielded by the generator function.
- task.close() - Raises a GeneratorExit at the point where the generator function was paused.

Exceptions
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

If a task schedules another task, which way should the reference go? Does the 
child task decrement the parent counter or vise versa?

TODOs
- NEXT STEP: Remove jobs from tasks when their ref counter is 0.
  BUG: Right now not removing regular functions from the task dir.

- NEXT STEP: Try with hierarchy of tasks.
  At the moment, tasks are continued to be ran by adding them back to the queue.
  In a hierarchy, the preferred behavior is to run the dependencies and then, 
  revisit the parent job. Needs a bit more sophistication. Like, the queue
  mechanism can be used for serving up tasks that are ready to run, but 
  there needs to be something else that is detecting what can be ran.
  This is were I think a priority queue based on the # of references could 
  possibly be helpful.
"""


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

# TODO: Rename
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
    print(f'Starting Task: {task_id}')
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
    print(f'Resume Task: {task_id}')
    pending_task: PendingTask = self._tasks[task_id]    
    try: 
      next(pending_task.coroutine)
      self._ready_to_resume_queue.append(task_id)
    except StopIteration:
      # This task is complete so remove it. 
      self.remove_task(task_id)


  # Alternative to the run method.
  def consume(self):
    print('In Consume')
    print(f'Tasks: {len(self._tasks)}')
    print(f'Queue Depth: {len(self._ready_to_initialize_queue)}')
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
    print(f'Attempting to remove task {task_id}')
    if task_id in self._tasks:
      finished_task = self._tasks[task_id]
      # If the completed coroutine has a parent, decrement it's reference counter.
      self._remove_reference(finished_task.parent_id)
      print(f'Removed Task: {task_id}')
      del self._tasks[task_id]

  def _remove_reference(self, task_id: TaskId) -> None:
    """ Remove a reference to a task.
    Decrements a task's reference counter. If the counter gets to zero, places 
    it on the ready to run queue.
    """
    if task_id and task_id in self._tasks:
      task = self._tasks[task_id]
      task.waiting_on_count -= 1
      if task.waiting_on_count <= 0:
        self._ready_to_initialize_queue.append(task_id)

def count_down(name: str, count = 5, *args, **kargs) -> None:
  try:
    while count > 0:
      print(f'{name} Count Down: {count}')
      count -= 1
      yield
  finally:
    print(f'{name} finalized')

def regular_function(*args, **kargs) -> None:
  print('Regular function. No yield expression.')

def uc_rerunning(ts: TaskScheduler):
  """Use case: Keep re-running a paused task if the coroutine allows it."""
  ts.add_task(count_down('A', 10))
  ts.add_task(count_down('B', 5))
  ts.add_task(regular_function)
  ts.add_task(count_down('C', 22))
  ts.add_task(count_down('D', 15))

# BUG I need to have the the current coroutine's task_id to pass in to the 
# child tasks. :(
"""
I really don't want it passed in explicitly. I'd prefer to inject it somehow.
Having the task scheduler, task_id and parent id available when the task runs
seems appropriate. 
Doing that on task.send(..) seems really problamatic. 
With the current design each task would need to yield once to get the context stuff.
context = yield

Need to play around with this.
https://stackoverflow.com/questions/5063607/is-there-a-generic-way-for-a-function-to-reference-itself

BUG I think part of the problem is that I'm thinking this is a coroutine, but 
since I'm not using the yield keyword it's just a function.
Calling send(context) doesn't solve my problem.
https://stackoverflow.com/questions/19892204/send-method-using-generator-still-trying-to-understand-the-send-method-and-quir

I think a better way to handle this is to:
1.  Have TaskScheduler.add_task take in the parameters that the generator needs 
    to be bound to. 
2.  Extend the args to include a reference to the scheduler and task ID. 
3.  Have the scheduler initialize the coroutine. Then we're back to always just 
    calling next(task).

The additional complexity of this approach is that the scheduler needs to track 
if a coroutine has been started or not.

Options for Tracking started vs running coroutines:
1.  Have a "started: bool" property on the PendingTask class. 
    This will require a branch in the consume() method to determine to initialize 
    the coroutine or to just call next().

2.  The TaskScheduler leverages multiple queues for different types of operations.
    Have individual queues for:
    - Coroutines that haven't been run yet.
    - Coroutines that are paused and need to be continued. Could have another 
      one for tasks that need to be purged.
    - Tasks that are just simple functions (no yield)
    This approach could potentially remove most branching but will require either
    multiple consume() style methods (and some way to prioritize queues) or 
    have more branching around add_task()
"""
   
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

  # uc_rerunning(ts)
  uc_hierarchy(ts)

  time.sleep(1)
  logging.info(f'Exiting the app.')
  logging.info(f'Tasks: {len(ts._tasks)}')


# NOTE
"""
I feel like I'm swimming upstream on this. 

Next Steps:
- Finish this little experiment.
- Create a new benchmark file. 
- Try doing basically the same thing but using the asynco module.
- Try defining tasks with the async keyword.
- Evaluate asyncio.create_task and asynco.gather

def blah():
  try:
    print('initial')
    y = yield
    print(y)
    z = yield
    print(z)
  finally:
    print('finalized')
"""