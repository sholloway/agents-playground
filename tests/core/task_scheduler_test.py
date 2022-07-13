from pytest_mock import MockFixture

from agents_playground.core.task_scheduler import (
  time_query, 
  TaskMetric,
  Counter,
  PendingTask,
  TaskScheduler
)

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
    ts.add_task(ts)
    ts.add_task(ts)
    ts.add_task(ts)
    ts.add_task(ts)
    assert len(ts._ready_to_initialize_queue) == 4
    assert ts._pending_tasks.value() == 4
    assert len(ts._tasks) == 4

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

    # TODO: Not done testing add_task. Need to deal with the conditionals.

    # TODO: There may be a bug in the task scheduler. 
    # Need to test how it handles running consume when a task 
    # Is ready to be initialized but has been removed.
    # removing a task currently doesn't reduce the self._pending_tasks
    # counter or the self._ready_to_initialize_queue, self._ready_to_resume_queue
    # queues. 

  
