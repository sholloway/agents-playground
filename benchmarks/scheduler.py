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
- Currently the uc_frame_based isn't written correctly. Need a way to tell 
  the scheduler to stop after the allocated frame time is done. It may be easier
  to just create batches of tasks and observe how long they take. ND does ~134 
  per worker thread per frame.
- Need a way to increase the size of the matplotlib Plots both vertically and 
  horizontally.

TODOs
- Add priorities. High priority should go to the front of the line.
- Finish this little experiment.
- Add benchmarking measurements to this. 
  - Measure the upper limit on the number of coroutines that can be processed like this.
  - Things to track:
    - [X] Queue Depth for each queue
      At what point does the queue depth become unable to be completed in a frame (16.67 ms)? 
    - [X]# Registered Tasks
    - [ ] Time to complete a task. Measured time from add_task to remove_task
    - [ ] Memory Utilization?
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
import random

# Setup Benchmarking
import gc
import sys
import time
from statistics import mean, quantiles
from matplotlib import pyplot as plt
from agents_playground.core.time_utilities import TimeInMS, TIME_PER_FRAME

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

metrics = {
  'ready_to_initialize_queue_depth': [], # Format: Tuple(frame: int, depth: int)
  'ready_to_resume_queue_depth': [], # Format: Tuple(frame: int, depth: int)
  'registered_tasks': [], # Format: Tuple(frame: int, tasks_count: int)
  'task_times': {} # Format: {task_id: TaskId, TaskMetric}
}

# Setup Logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

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
    self._task_counter = itertools.count(1)
    self._tasks: dict[TaskId, PendingTask] = dict()
    self._ready_to_initialize_queue: SelfPollingQueue = SelfPollingQueue(self._initialize_task)
    self._ready_to_resume_queue: SelfPollingQueue = SelfPollingQueue(self._resume_task)

  def _initialize_task(self, task_id: TaskId) -> None:
    logger.info(f'Starting Task: {task_id}')
    metrics['task_times'][task_id].started_time = time_query()
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
        metrics['task_times'][task_id].completed_time = time_query()
        self.remove_task(task_id)
    else: 
      # Dealing with a regular function. 
      # It's done so just remove it from the task registry.
      metrics['task_times'][task_id].completed_time = time_query()
      self.remove_task(task_id)

  def _resume_task(self, task_id: TaskId):
    # Note: Only coroutine/generator iterators can be resumed.
    logger.info(f'Resuming Task: {task_id}')
    pending_task: PendingTask = self._tasks[task_id]    
    try: 
      next(pending_task.coroutine)
      if pending_task.waiting_on_count <= 0:
        self._ready_to_resume_queue.append(task_id)
    except StopIteration:
      # This task is complete so remove it. 
      metrics['task_times'][task_id].completed_time = time_query()
      self.remove_task(task_id)

  def consume(self):
    logger.info('In Consume')
    logger.info(f'Tasks: {len(self._tasks)}')
    logger.info(f'Queue Depth: {len(self._ready_to_initialize_queue)}')
    frame = 0 # Just used for benchmarking.
    try:
      while True:
        can_read, _, _ = select.select([self._ready_to_initialize_queue, self._ready_to_resume_queue], [], [])
        # frame += 1
        frame = time_query()
        metrics['ready_to_initialize_queue_depth'].append((frame, len(self._ready_to_initialize_queue)))
        metrics['ready_to_resume_queue_depth'].append((frame, len(self._ready_to_resume_queue)))
        metrics['registered_tasks'].append((frame, len(self._tasks)))
        for q in can_read:
          q.process_item()
    except Exception as e:
      logger.exception('Caught an exception in the consume function')

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
    metrics['task_times'][task_id] = TaskMetric(time_query())

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
      metrics['task_times'][task_id].removed_time = time_query()
      # If the completed coroutine has a parent, decrement it's reference counter.
      self._remove_reference(finished_task.parent_id)
      del self._tasks[task_id]
      logger.info(f'Removed Task: {task_id}')

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
      logger.info(f'{name} Count Down: {count}')
      count -= 1
      yield
  finally:
    logger.info(f'{name} finalized')

def regular_function(*args, **kargs) -> None:
  logger.info('Regular function. No yield expression.')

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

  logger.info('Starting call_four_coroutines')
  logger.debug(f'Args: {args}')
  logger.debug(f'KWArgs: {kwargs}')
  name = kwargs['name']
  task_id = kwargs['task_id']
  ts = kwargs['ts']

  try:
    ts.add_task(count_down, ['A', 10], parent_id=task_id)
    ts.add_task(count_down, ['B', 5], parent_id=task_id)
    ts.add_task(regular_function, parent_id=task_id)
    yield
  finally:
    logger.info(f'{name} finalized')

def uc_hierarchy(ts: TaskScheduler):
  """Use Case: A coroutine adds other coroutines that must be completed before it itself can be processed again."""
  ts.add_task(call_four_coroutines, [], { 'name': 'call_four_coroutines'})

def uc_frame_based(ts: TaskScheduler):
  """Attempt to simulated a maximized simulation frame.
  
  If the target FPS is 60 Hz then a frame takes 16.67ms. This use case constrains
  the run time to a single frame.
  """
  start_time: TimeInMS = time_query()
  stop_time: TimeInMS = start_time + TIME_PER_FRAME
  current_time = start_time
  while current_time < stop_time:
    ts.add_task(count_down, ('A', random.randint(0,10)))
    current_time = time_query()


def find_task_metric_deltas(t: TaskMetric):
  return (
    t.started_time - t.registered_time, # time_to_start
    t.completed_time - t.started_time, # time_to_process
    t.removed_time - t.registered_time # time_to_complete
  )

# Looking at https://github.com/benmoran56/esper/blob/master/examples/benchmark.py
# For inspiration.
def plot_benchmarks():
  logger.info('Plotting Benchmarks')
  fig, (stats, task_times, queues) = plt.subplots(nrows=3, ncols=1)
  
  fig.suptitle('Task Scheduling Benchmarks')

  # Setup the Tasks Timing Plot 
  # Try drawing a horizontal line for each task. 
  # Y-Axis: The Task ID
  # X-Axis: Start and stop time.

  # filter out any tasks that weren't complete
  finished_tasks = filter(lambda m: m.complete() == True, metrics['task_times'].values())
  time_to_start, time_to_process, time_to_complete = zip(*map(find_task_metric_deltas, finished_tasks))
  avg_time_to_start = round(mean(time_to_start), 3)
  avg_processing_time = round(mean(time_to_process), 3)
  avg_time_to_completion = round(mean(time_to_complete), 3)

  # Find the 90th percentiles
  p90_time_to_start = round(quantiles(sorted(time_to_start), n=10, method='inclusive')[8], 3)
  p90_processing_time = round(quantiles(sorted(time_to_process), n=10, method='inclusive')[8], 3)
  p90_time_to_completion = round(quantiles(sorted(time_to_complete), n=10, method='inclusive')[8], 3)

  cells = [
    [avg_time_to_start, p90_time_to_start],
    [avg_processing_time, p90_processing_time],
    [avg_time_to_completion, p90_time_to_completion]]

  columns_labels = ['Avg', 'P90']
  row_labels = ['Time To Start', 'Processing Time', 'Time To Completion']

  stats.set_title('Task Timing Stats (ms)')
  stats.axis('off')
  stats.axis('tight')
  stats.table(cellText=cells, colLabels=columns_labels, rowLabels=row_labels, loc='center', cellLoc='center', colWidths=[0.4, 0.4], edges='vertical')

  task_times.set_title('Task Timings')
  task_times.set_ylabel('Task ID')
  for task_id, task_metric in metrics['task_times'].items():
    y = [task_id, task_id, task_id, task_id]
    x = [task_metric.registered_time, task_metric.started_time, task_metric.completed_time, task_metric.removed_time]
    task_times.plot(x,y, markevery=1, marker='p')
  # task_times.set_xlabel('Process Time (ms)')
  # task_times.legend(loc='upper center')

  # Setup the queue benchmarks plot
  iqd_x, iqd_y = zip(*metrics['ready_to_initialize_queue_depth'])
  rqd_x, rqd_y = zip(*metrics['ready_to_resume_queue_depth'])
  rt_x, rt_y = zip(*metrics['registered_tasks'])
  queues.set_title('Queue Depths')
  queues.plot(iqd_x, iqd_y, color='red', label='Ready to Initialize')
  queues.plot(rqd_x, rqd_y, color='green', label='Ready to Resume')
  queues.plot(rt_x, rt_y, color='blue', label='Registered Tasks')
  queues.set_ylabel('Count')
  queues.set_xlabel('Process Time (ms)')
  queues.legend(loc='center left', bbox_to_anchor=(1,0.5))

  # Add the task stats as text.
  # text_x = 0.7
  # text_y = 0.84
  # text_line = 0.03
  # text_size = 10
  # precision = 3
  # plt.figtext(text_x, text_y, f'Task Timing Stats (ms) Avg|P90', fontsize=text_size)
  # plt.figtext(text_x, text_y - (text_line * 1), f'Time To Start: {round(avg_time_to_start, precision)} | {round(p90_time_to_start, 3)}', fontsize=text_size)
  # plt.figtext(text_x, text_y - (text_line * 2), f'Processing Time: {round(avg_processing_time, precision)}| {round(p90_processing_time, 3)}', fontsize=text_size)
  # plt.figtext(text_x, text_y - (text_line * 3), f'Time To Completion: {round(avg_time_to_completion, precision)}| {round(p90_time_to_completion, 3)}', fontsize=text_size)
  
  plt.tight_layout()
  plt.show()
  logger.info('Done Plotting')

if __name__ == '__main__':
  ts = TaskScheduler()

  schedule_thread = threading.Thread(
    name="schedule_thread", 
    target=ts.consume, 
    args=(), 
    daemon=True
  )
  schedule_thread.start()

  # uc_rerunning(ts)
  # uc_hierarchy(ts)
  uc_frame_based(ts)

  time.sleep(1)
  plot_benchmarks()
  logger.info(f'Tasks: {len(ts._tasks)}')
  logger.info(f'Exiting the app.')