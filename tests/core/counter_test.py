from agents_playground.counter.counter import Counter, CounterBuilder


class TestCounter:
    def test_counter_increment(self) -> None:
        count_up = CounterBuilder.integer_counter_with_defaults(
            start=3, increment_step=2
        )
        assert count_up.value() == 3
        assert count_up.increment() == 5
        assert count_up.increment() == 7
        assert count_up.increment() == 9
        assert count_up.value() == 9
        count_up.reset()
        assert count_up.value() == 3

    def test_counter_decrement(self) -> None:
        count_down = CounterBuilder.integer_counter_with_defaults(
            start=15, decrement_step=5
        )
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
        count_down = CounterBuilder.integer_counter_with_defaults(
            start=10, decrement_step=1, min_value=7
        )
        assert count_down.decrement() == 9
        assert count_down.decrement() == 8
        assert count_down.decrement() == 7
        assert count_down.decrement() == 7
        assert count_down.decrement() == 7

    def test_min_value_check(self) -> None:
        count_down = CounterBuilder.integer_counter_with_defaults(
            start=1004, decrement_step=1, min_value=1000
        )
        assert not count_down.at_min_value()

        assert count_down.decrement() == 1003 and not count_down.at_min_value()
        assert count_down.decrement() == 1002 and not count_down.at_min_value()
        assert count_down.decrement() == 1001 and not count_down.at_min_value()
        assert count_down.decrement() == 1000 and count_down.at_min_value()

    def test_constrained_increment(self) -> None:
        count_up = CounterBuilder.integer_counter_with_defaults(
            start=-4, decrement_step=1, max_value=0
        )
        assert count_up.increment() == -3
        assert count_up.increment() == -2
        assert count_up.increment() == -1
        assert count_up.increment() == 0
        assert count_up.increment() == 0
        assert count_up.increment() == 0

    def test_max_value_check(self) -> None:
        count_up = CounterBuilder.integer_counter_with_defaults(
            start=-4, decrement_step=1, max_value=0
        )
        assert count_up.increment() == -3 and not count_up.at_max_value()
        assert count_up.increment() == -2 and not count_up.at_max_value()
        assert count_up.increment() == -1 and not count_up.at_max_value()
        assert count_up.increment() == 0 and count_up.at_max_value()
