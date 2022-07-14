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

  def test_counter_increment(self, mocker: MockFixture) -> None:
    count_up = Counter(start = 3, increment_step=2)
    assert count_up.value() == 3

    assert count_up.increment() == 5
    assert count_up.increment() == 7
    assert count_up.increment() == 9
    assert count_up.value() == 9
    count_up.reset()
    assert count_up.value() == 3

  def test_counter_decrement(self, mocker: MockFixture) -> None:
    count_down = Counter(start = 15, decrement_step=5)
    assert count_down.value() == 15

    assert count_down.decrement() == 10
    assert count_down.decrement() == 5
    assert count_down.decrement() == 0
    assert count_down.value() == 0
    assert count_down.decrement() == -5
    assert count_down.decrement() == -10
    assert count_down.decrement() == -15
    count_down.reset()
    assert count_down.value() == 15

  def test_add_task(self, mocker: MockFixture) -> None:
    fake_task = lambda: True
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
    fake_task = lambda: True
    ts = TaskScheduler()
    assert ts.add_task(ts) != -1
    assert ts._stopped == False

    ts.stop()
    assert ts._stopped
    assert ts.add_task(ts) == -1

    ts.start()
    assert ts.add_task(ts) != -1


  # TODO: Not done testing add_task. Need to deal with the conditionals.
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

    # TODO: There may be a bug in the task scheduler. 
    # Need to test how it handles running consume when a task 
    # Is ready to be initialized but has been removed.
    # removing a task currently doesn't reduce the self._pending_tasks
    # counter or the self._ready_to_initialize_queue, self._ready_to_resume_queue
    # queues. 

  
