from agents_playground.core.counter import Counter

class TestCounter:
  def test_counter_increment(self) -> None:
    count_up = Counter(start = 3, increment_step=2)
    assert count_up.value() == 3
    assert count_up.increment() == 5
    assert count_up.increment() == 7
    assert count_up.increment() == 9
    assert count_up.value() == 9
    count_up.reset()
    assert count_up.value() == 3

  def test_counter_decrement(self) -> None:
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

  def test_constrained_decrement(self) -> None:
    count_down = Counter(start = 10, decrement_step=1, min_value = 7)
    assert count_down.decrement() == 9
    assert count_down.decrement() == 8
    assert count_down.decrement() == 7
    assert count_down.decrement() == 7
    assert count_down.decrement() == 7

  def test_min_value_check(self) -> None:
    count_down = Counter(start = 1004, decrement_step=1, min_value = 1000)
    assert not count_down.at_min_value() 

    assert count_down.decrement() == 1003 and not count_down.at_min_value()
    assert count_down.decrement() == 1002 and not count_down.at_min_value()
    assert count_down.decrement() == 1001 and not count_down.at_min_value()
    assert count_down.decrement() == 1000 and count_down.at_min_value()

  def test_constrained_increment(self) -> None:
    count_up = Counter(start = -4, decrement_step=1, max_value = 0)
    count_up.increment() == -3
    count_up.increment() == -2
    count_up.increment() == -1
    count_up.increment() == 0
    count_up.increment() == 0
    count_up.increment() == 0

  def test_max_value_check(self) -> None:
    count_up = Counter(start = -4, decrement_step=1, max_value = 0)
    count_up.increment() == -3 and not count_up.at_max_value()
    count_up.increment() == -2 and not count_up.at_max_value()
    count_up.increment() == -1 and not count_up.at_max_value()
    count_up.increment() == 0 and count_up.at_max_value()