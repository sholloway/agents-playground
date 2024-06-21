from agents_playground.counter.counter import Counter, CounterBuilder

class IdGenerator:
    """
    Creates incrementing IDs.
    """
    def __init__(self, start: int = 0) -> None:
        self._counter: Counter[int] = CounterBuilder.integer_counter_with_defaults(start=start)

    def next(self) -> int:
        return self._counter.increment()


global_id_generator = IdGenerator()


def next_id() -> int:
    return global_id_generator.next()
