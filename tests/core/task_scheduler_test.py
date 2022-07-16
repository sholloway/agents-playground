from typing import Generator
from pytest_mock import MockFixture

from agents_playground.core.task_scheduler import (
  ScheduleTraps,
  time_query, 
  TaskMetric,
  Counter,
  PendingTask,
  TaskScheduler
)

# TODO: I want a way to spy on a coroutine...
def simple_coroutine(*args, **kwargs) -> Generator:
  # assert the default things passed by the scheduler?
  try:
    while True:
      # Spy: Do the work here.
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    pass # spy
  finally:
    pass #spy

def coroutine_with_params(*args, **kwargs) -> Generator:
  try:
    while True:
      # assert the default things passed by the scheduler
      assert args == ('a','b','c')
      assert 'd' in kwargs, "d not found in kwargs"
      assert 'e' in kwargs, "e not found in kwargs"
      assert 'f' in kwargs, "f not found in kwargs"
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    pass # spy
  finally:
    pass #spy

class TestTaskScheduler:
  def test_time_query_converts_to_ms(self, mocker: MockFixture) -> None:
    mocker.patch('time.process_time', return_value = 1)
    current_time = time_query()
    assert current_time == 1000

  def test_test_metric_marked_complete(self, mocker: MockFixture) -> None:
    default_metric_incomplete = TaskMetric(1)
    assert default_metric_incomplete.complete() == False
    
    start_time_not_set_metric_incomplete = TaskMetric(1)
    start_time_not_set_metric_incomplete.completed_time = 1
    start_time_not_set_metric_incomplete.removed_time = 1
    assert start_time_not_set_metric_incomplete.complete() == False

    completed_time_not_set_metric_incomplete = TaskMetric(1)
    completed_time_not_set_metric_incomplete.started_time = 1
    completed_time_not_set_metric_incomplete.removed_time = 1
    assert completed_time_not_set_metric_incomplete.complete() == False

    removed_time_not_set_metric_incomplete = TaskMetric(1)
    removed_time_not_set_metric_incomplete.started_time = 1
    removed_time_not_set_metric_incomplete.completed_time = 1
    assert removed_time_not_set_metric_incomplete.complete() == False

    completed_metric = TaskMetric(1)
    completed_metric.started_time = 1
    completed_metric.completed_time = 1
    completed_metric.removed_time = 1
    assert completed_metric.complete() == True

  def test_add_task(self, mocker: MockFixture) -> None:
    fake_task = mocker.Mock()
    ts = TaskScheduler()
    assert len(ts._ready_to_initialize_queue) == 0
    assert ts.add_task(ts) != -1
    assert ts.add_task(ts) != -1
    assert ts.add_task(ts) != -1
    assert ts.add_task(ts) != -1
    assert len(ts._ready_to_initialize_queue) == 4
    assert ts._pending_tasks.value() == 4
    assert len(ts._tasks) == 4

  def test_cannot_add_tasks_when_stopped(self, mocker: MockFixture) -> None:
    fake_task = mocker.Mock()
    ts = TaskScheduler()
    assert ts.add_task(ts) != -1
    assert ts._stopped == False

    ts.stop()
    assert ts._stopped
    assert ts.add_task(ts) == -1

    ts.start()
    assert ts.add_task(ts) != -1

  def test_task_parentage(self, mocker: MockFixture) -> None:
    fake_task = lambda: True
    ts = TaskScheduler()

    parent_id = ts.add_task(fake_task)
    assert ts._tasks[parent_id].waiting_on_count == 0

    child_id = ts.add_task(fake_task,parent_id=parent_id)
    assert ts._tasks[parent_id].waiting_on_count == 1

  def test_remove_task(self, mocker: MockFixture) -> None:
    fake_task = lambda: True
    ts = TaskScheduler()
    t1 = ts.add_task(ts)
    t2 = ts.add_task(ts)
    t3 = ts.add_task(ts)
    t4 = ts.add_task(ts)
    assert len(ts._ready_to_initialize_queue) == 4

    ts.remove_task(t3)

    assert len(ts._tasks) == 3

  # The scheduler can handle invoking simple functions or resumable coroutines.
  # Simple functions are run when they're consumed from the ready_to_initialize_queue.
  def test_running_simple_functions(self, mocker: MockFixture) -> None:
    task1 = mocker.Mock()
    task2 = mocker.Mock()
    task3 = mocker.Mock()
    ts = TaskScheduler()
    
    ts.add_task(task1)
    ts.add_task(task2)
    ts.add_task(task3)

    ts.consume()

    task1.assert_called_once()
    task2.assert_called_once()
    task3.assert_called_once()
  
  # The scheduler can handle invoking simple functions or resumable coroutines.
  # Coroutines are initialized when consumed from the ready_to_initialize_queue.
  # They are run when they're consumed from the ready_to_resume_queue.
  def test_running_resumable_coroutine(self, mocker: MockFixture) -> None:
    coroutine1 = simple_coroutine
    ts = TaskScheduler()
    taskId = ts.add_task(coroutine1)
    assert len(ts._ready_to_initialize_queue) == 1
    assert len(ts._ready_to_resume_queue) == 0
    assert len(ts._hold_for_next_frame) == 0
  
    # The first time consume is ran, items are pulled from the ready_to_initialize_queue.
    ts.consume()
    assert len(ts._ready_to_initialize_queue) == 0
    assert len(ts._ready_to_resume_queue) == 0
    assert len(ts._hold_for_next_frame) == 1

    # Resumable items must be moved from the _hold_for_next_frame to _ready_to_resume_queue.
    ts.queue_holding_tasks()
    assert len(ts._ready_to_initialize_queue) == 0
    assert len(ts._ready_to_resume_queue) == 1
    assert len(ts._hold_for_next_frame) == 0

    # The 2nd consume pulls from the _ready_to_resume_queue.
    # Since the coroutine doesn't have an exit condition it is queued up again in 
    # the hold_for_next_frame dequeue.
    ts.consume()
    assert len(ts._ready_to_initialize_queue) == 0
    assert len(ts._ready_to_resume_queue) == 0
    assert len(ts._hold_for_next_frame) == 1

  # - Test how args are passed to functions. 
  def test_passing_args_to_coroutines(self, mocker: MockFixture) -> None:
    ts = TaskScheduler()
    my_args = ['a','b','c']
    my_dict = {'d':1, 'e':2, 'f':3}
    tid = ts.add_task(coroutine_with_params, args=my_args, kwargs = my_dict)
    
    assert tid != -1
    pending_task: PendingTask = ts._tasks[tid]
    assert pending_task.args == my_args
    assert pending_task.kwargs == my_dict

    ts.consume() # Consume the task which also assert the args are passed in.
    ts.queue_holding_tasks()
    ts.consume()

  def test_coroutine_dependencies(self, mocker: MockFixture) -> None:
    task_ran_order = []
    parent_task = lambda *args, **kwargs: task_ran_order.append(kwargs['task_id'])
    kid_a_task = lambda *args, **kwargs: task_ran_order.append(kwargs['task_id'])
    kid_b_task = lambda *args, **kwargs: task_ran_order.append(kwargs['task_id'])
    ts = TaskScheduler()
    parent = ts.add_task(parent_task)
    kid_a = ts.add_task(kid_a_task, parent_id=parent)
    kid_b = ts.add_task(kid_b_task, parent_id=parent)

    assert ts._tasks[parent].waiting_on_count == 2
    assert ts._tasks[kid_a].waiting_on_count == 0
    assert ts._tasks[kid_b].waiting_on_count == 0

    ts.consume()

    assert task_ran_order == [kid_a, kid_b, parent]

  """
  TODO
  - Fix PendingTask.waiting_on_count. Make it a constrained counter. Change all <= to a readable function call.
  - Perhaps expand the Counter class to have optional upper and lower bounds.
  - Perhaps have a method on Counter like my_counter.at_max(), my_counter.at_min()
  - Need to get tests around the Counter class directly. 
  """