# Run With:
# poetry run python ./benchmarks/scheduler.py
# Debug With:
# PYTHONBREAKPOINT="pudb.set_trace" poetry run python -X dev ./benchmarks/scheduler.py


from collections import deque
from dataclasses import dataclass
from enum import Enum
import itertools
from telnetlib import TSPEED
from typing import Any, Callable, List, Optional
import socket
import select
import threading
import time

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
  # The number of tasks this task needs to complete before it can.
  waiting_on_count: TaskRefCounter 
  task: Task

# TODO: Rename
class SelfPollingQueue(deque):
  def __init__(self) -> None:
    super().__init__()
    self._put_socket, self._get_socket = socket.socketpair()

  def fileno(self):
    return self._get_socket.fileno()

  def append(self, item: Any) -> None:
    super().append(item)
    self._put_socket.send(b'x')
    
  def popleft(self) -> Any:
    self._get_socket.recv(1)
    return super().popleft()


class TaskPriority(Enum):
  HIGH = 0
  NORMAL = 1
  LOW = 2

class TaskScheduler:
  def __init__(self) -> None:
    self._task_counter = itertools.count()
    self._tasks: dict[TaskId, PendingTask] = dict()
    self._queue: SelfPollingQueue = SelfPollingQueue()
    # - timed_queue: PriorityQueue
    # self._high_priority_queue: LILOQueue
    # self._normal_priority_queue: FIFOQueue
    # self._low_priority_queue: FIFOQueue

  def run(self):
    while self._queue:
      task_id = self._queue.popleft()
      pending_task: PendingTask = self._tasks[task_id]
      if hasattr(pending_task.task, '__next__'): #coroutine
        try:
          next(pending_task.task)
          self._queue.append(task_id)
        except StopIteration:
          pass
      else: # Regular function
        pending_task.task()

  # Alternative to the run method.
  def consume(self):
    print('In Consume')
    print(f'Tasks: {len(self._tasks)}')
    print(f'Queue Depth: {len(self._queue)}')
    try:
      while True:
        can_read, _, _ = select.select([self._queue], [], [])
        for q in can_read:
          task_id = q.popleft()
          pending_task: PendingTask = self._tasks[task_id]
          if hasattr(pending_task.task, '__next__'): #coroutine
            try:
              next(pending_task.task)
              q.append(task_id)
            except StopIteration:
              # This task is complete so remove it. 
              self.remove_task(task_id)
          else: # Regular function
            pending_task.task()
    except Exception as e:
      print('Caught an exception in the consume function')
      print(e)

  def add_task(self, 
    task: Callable, 
    parent_id: Optional[TaskId] = None, 
    priority: TaskPriority = TaskPriority.NORMAL) -> TaskId:
    """Register a task to be run with the scheduler.

    """
    task_id = next(self._task_counter)
    self._tasks[task_id] = PendingTask(task_id, parent_id, 0, task)
    if parent_id in self._tasks:
      self._tasks[parent_id].waiting_on_count += 1

    # TODO Will eventually use the priority parameter here.
    # Is a different data structure required here? (e.g. Priority Queue)
    self._queue.append(task_id)
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
        self._queue.append(task_id)

def count_down(name: str, count = 5) -> None:
  try:
    while count > 0:
      print(f'{name} Count Down: {count}')
      count -= 1
      yield
  finally:
    print(f'{name} finalized')

def regular_function() -> None:
  print('Regular function. No yield expression.')

def uc_rerunning(ts: TaskScheduler):
  """Use case: Keep re-running a paused task if the coroutine allows it."""
  ts.add_task(count_down('A', 10))
  ts.add_task(count_down('B', 5))
  ts.add_task(regular_function)
  ts.add_task(count_down('C', 22))
  ts.add_task(count_down('D', 15))

def call_four_coroutines(name: str, ts: TaskScheduler):
  # BUG I need to have the the current coroutine's task_id to pass in to the 
  # child tasks. :(
  # I really don't want it passed in explicitly. I'd prefer to inject it somehow.
  # Having the task scheduler, task_id and parent id available when the task runs
  # seems appropriate. 
  # Doing that on task.send(..) seems really problamatic. 
  # With the current design each task would need to yield once to get the context stuff.
  # context = yield
  # 
  # Need to play around with this.
  try:
    ts.add_task(count_down('A', 10), 0, TaskPriority.NORMAL)
    ts.add_task(count_down('B', 5), 0, TaskPriority.NORMAL)
    ts.add_task(regular_function, 0)
  finally:
    print(f'{name} finalized')

def uc_hierarchy(ts: TaskScheduler):
  """Use Case: A coroutine adds other coroutines that must be completed before it itself can be processed again."""
  args=[]
  kwargs = {}
  ts.add_task(call_four_coroutines("Top Coroutine", ts), 1, TaskPriority.NORMAL, args, kwargs)

if __name__ == '__main__':
  ts = TaskScheduler()

  schedule_thread = threading.Thread(
    name="schedule_thread", 
    target=ts.consume, 
    args=(), 
    daemon=True
  )
  schedule_thread.start()

  uc_rerunning(ts)
  # uc_hierarchy(ts)

  time.sleep(1)
  print(f'Exiting the app.')
  print(f'Tasks: {len(ts._tasks)}')