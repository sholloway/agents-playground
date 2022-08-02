# Run With:
# poetry run python ./benchmarks/scheduler.py

# Debug With:
# PYTHONBREAKPOINT="pudb.set_trace" poetry run python -X dev ./benchmarks/scheduler.py

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import random
from statistics import mean, quantiles
import threading
from typing import Dict

from matplotlib import pyplot as plt

from agents_playground.core.task_scheduler import TaskMetric, TaskScheduler
from agents_playground.core.time_utilities import TimeInMS, TIME_PER_FRAME
from agents_playground.sys.logger import get_default_logger, setup_logging

# sys.getallocatedblocks()
# sys.getrefcount(object)

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
- task.throw(...) - Raises an exception of type type at the point where the 
  generator was paused, and returns the next value yielded by the generator function.
- task.close() - Raises a GeneratorExit at the point where the generator function 
  was paused.

They can Throw Exceptions:
- StopIteration - https://docs.python.org/3.9/library/exceptions.html#StopIteration
  Raised when the generator naturally ends (if it does).
- GeneratorExit - https://docs.python.org/3.9/library/exceptions.html#GeneratorExit
  Raised by generator.close()

*Example*
def task(value = None):
  try:
    while True:
      # Value will be set to the value passed in by send(...).
      value = yield f'Hello {value}'
  catch GeneratorExit:
    print('Someone told me to stop.')
  finally:
    print('This is ran when task.close() is called.')

*Reference Counting*
The gist of referencing counting is that every item has an associated counter.
This counter tracks how many things refer to that item. When the counter 
is 0 there are no other items that need the item to exist. 

If a task spawns a blocking subtask, then by passing in the parent's task_id to 
add_tasks a reference counter will prevent the parent task from running again 
until the child tasks have completed. Non-blocking tasks simply don't reference
the parent task's id.

BUGs
- None at the moment

TODOs
- [X] Change the _resume_task() function to use send() rather than next(). 
  One thought is to pass in the FrameParams style object at that point or something
  as simple as the resume timestamp. 
- [ ] Add priorities. High priority should go to the front of the line.
- [X] Add Platfrom to the log output using sys.platform and os.name
- [X] Add the python type (cpython) and version to the benchmark/log output using sys.implementation and sys.version_info
- [ ] Need to address passing data between tasks. Look at the Naughty Dog concept 
  of FrameParams. Consider ECS and Entity-Component in the context of the TaskScheduler.
- One of the big limitations of this approach is all of the jobs are constrained
  to a single thread running on a single core. 
  A thought is to spin up "worker processes and assign tasks to them. Once a 
  task is started by a worker then it would be "pinned" to that worker.
- [X] I want to understand the memory consumption of using all of these generators.  
  However, the size of a dictionary is just the pointers so inspecting the size
  of self._tasks won't give it to me in a single call. I've added a more robust 
  getsize function but need to dig deeper on how generators and function pointers
  should be measured.
- Watch David M. Beazley talks on coroutines before doing much else. 
  http://www.dabeaz.com/generators-uk/
  [X] Video: https://www.youtube.com/watch?v=Z_OAlIhXziw
  [X] Slides: http://www.dabeaz.com/coroutines/Coroutines.pdf
  All Videos: https://www.youtube.com/user/dabeazllc/videos
- Go through to get a list of features (Does it make sense
  to adopt one of these?):
  - [X] https://github.com/dabeaz/curio
  - [ ] asyncio
  - [ ] Stackless
  - [ ] PyPy
  - [ ] Cogen
  - [ ] MultiTask
  - [ ] Eventlet
  - [ ] Kamaelia 
"""

setup_logging('DEBUG')
logger = get_default_logger()
logging.getLogger('matplotlib').setLevel(logging.WARNING)

def count_down(name: str, count = 5, *args, **kargs) -> None:
  try:
    # logger.info(f'Countdown Task {name} Started')
    while count > 0:
      # logger.info(f'{name} Count Down: {count}')
      count -= 1
      yield
  finally:
    # logger.info(f'Task {name} finalized')
    return

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

def uc_bulk(ts: TaskScheduler, num_of_tasks: int) -> None:
  for i in range(num_of_tasks):
    ts.add_task(count_down, (i, random.randint(0,10)))
  ts.stop()

def find_task_metric_deltas(t: TaskMetric):
  return (
    t.started_time - t.registered_time, # time_to_start
    t.completed_time - t.started_time, # time_to_process
    t.removed_time - t.registered_time # time_to_complete
  )
  
# Looking at https://github.com/benmoran56/esper/blob/master/examples/benchmark.py
# For inspiration.
def plot_benchmarks(metrics: Dict):
  logger.info('Plotting Benchmarks')
  #define plot size for all plots

  plt.rcParams['figure.figsize'] = [10, 10]
  fig, (stats, task_times, queues, memory) = plt.subplots(nrows=4, ncols=1)
  
  fig.suptitle('Task Scheduling Benchmarks')

  # Setup the Tasks Timing Plot 
  # Try drawing a horizontal line for each task. 
  # Y-Axis: The Task ID
  # X-Axis: Start and stop time.

  # Calculate Simulation Duration (ms)
  sim_duration = metrics['sim_stop_time'] - metrics['sim_start_time']

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

  stats.set_title(f'Task Timing Stats over {sim_duration} ms')
  stats.axis('off')
  stats.axis('tight')
  stats.table(cellText=cells, colLabels=columns_labels, rowLabels=row_labels, loc='center', cellLoc='center', colWidths=[0.4, 0.4], edges='vertical')

  task_times.set_title('Task Timings')
  task_times.set_ylabel('Task ID')
  for task_id, task_metric in metrics['task_times'].items():
    y = [task_id, task_id, task_id, task_id]
    x = [task_metric.registered_time, task_metric.started_time, task_metric.completed_time, task_metric.removed_time]
    task_times.plot(x,y, markevery=1, marker='p')
  
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

  tr_x, tr_y = zip(*metrics['register_memory'])
  memory.set_title('Task Registry Memory Consumption')
  memory.plot(tr_x, tr_y, color='red', label='Task Register')
  memory.set_ylabel('Memory (bytes)')
  memory.set_xlabel('Process Time (ms)')
  
  plt.tight_layout()
  # plt.show()
  fig.savefig('benchmark.png', bbox_inches='tight')   
  plt.close(fig)
  logger.info('Done Plotting')

if __name__ == '__main__':
  ts = TaskScheduler(profile=True)

  # uc_rerunning(ts)
  # uc_hierarchy(ts)
  # uc_frame_based(ts)
  uc_bulk(ts, 100)
  
  schedule_thread = threading.Thread(
    name="schedule_thread", 
    target=ts.consume, 
    args=(), 
    daemon=False
  )

  schedule_thread.start()
  schedule_thread.join() #waiting for completion
  
  plot_benchmarks(ts.metrics())
  
  assert len(ts._tasks_store) == 0, "All the tasks should be done."
  
  logger.info(f'Exiting the app.')