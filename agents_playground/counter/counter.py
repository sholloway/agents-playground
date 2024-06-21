from __future__ import annotations

from decimal import Decimal
from typing import Callable, Generic, TypeVar, cast
from math import inf as INFINITY

NEGATIVE_INFINITY = -INFINITY


def do_nothing(**kwargs) -> None:
    """A pass through function used to simplify the Counter defaults."""
    return


PrecisionType = TypeVar("PrecisionType", int, float, Decimal)


class Counter(Generic[PrecisionType]):
    """
    An actionable counter. Can be used to count up or down and optionally take
    action when targets are reached.

    Args:
      - start: The value to start the counter at.
      - increment_step: The size of step to count up.
      - decrement_step: The size of step to count down.
      - min_value: The lowest value (inclusive) the counter can count down to.
      - max_value: The highest value (inclusive) the counter can count up to.
      - min_value_reached: An optional callable to invoke when the minimum value is reached.
      - increment_action: An optional callable to invoke when the counter is incremented.
      - decrement_action: An optional callable to invoke when the counter is decremented.
    """

    def __init__(
        self,
        start: PrecisionType,
        increment_step: PrecisionType,
        decrement_step: PrecisionType,
        min_value: PrecisionType,
        max_value: PrecisionType,
        min_value_reached: Callable = do_nothing,
        max_value_reached: Callable = do_nothing,
        increment_action: Callable = do_nothing,
        decrement_action: Callable = do_nothing,
    ) -> None:
        super().__init__()
        self._start: PrecisionType = start
        self._value: PrecisionType = start
        self._increment_step: PrecisionType = increment_step
        self._decrement_step: PrecisionType = decrement_step
        self._min_value: PrecisionType = min_value
        self._max_value: PrecisionType = max_value

        self._min_value_reached: Callable = min_value_reached
        self._max_value_reached: Callable = max_value_reached
        self._increment_action: Callable = increment_action
        self._decrement_action: Callable = decrement_action

    @property
    def start(self: Counter[PrecisionType]) -> PrecisionType:
        return self._start

    @start.setter
    def start(self: Counter[PrecisionType], new_start: PrecisionType) -> None:
        self._start = new_start

    def increment(self: Counter[PrecisionType], **kwargs) -> PrecisionType:
        """Counts up by the step amount.

        Args:
          - kwargs: Named parameters that can be passed to the increment_action and
            max_value_reached action.

        Returns:
          The new value the counter is at.
        """
        if self._value < self._max_value:
            self._value = self._value + self._increment_step
            self._increment_action(**kwargs)
        else:
            self._max_value_reached(**kwargs)
        return self._value

    def decrement(self: Counter[PrecisionType], **kwargs) -> PrecisionType:
        """Counts down by the step amount.

        Args:
          - kwargs: Named parameters that can be passed to the decrement_action and
            min_value_reached action.

        Returns:
          The new value the counter is at.
        """
        if self._value > self._min_value:
            self._value = self._value - self._decrement_step
            self._decrement_action(**kwargs)
        else:
            self._min_value_reached(**kwargs)
        return self._value

    def value(self: Counter[PrecisionType]) -> PrecisionType:
        """A getter function for the counter's current value."""
        return self._value

    def set(self: Counter[PrecisionType], value: PrecisionType) -> None:
        """Set the active value."""
        self._value = value

    def reset(self: Counter[PrecisionType]) -> None:
        """Resets the counter to the start value."""
        self._value = self._start

    def at_min_value(self: Counter[PrecisionType]) -> bool:
        """Determines if the counter is at the lower threshold."""
        return self._value <= self._min_value

    def at_max_value(self: Counter[PrecisionType]) -> bool:
        """Determines if the counter is at the upper threshold."""
        return self._value >= self._max_value

    def __repr__(self: Counter[PrecisionType]) -> str:
        """An implementation of the dunder __repr__ method. Used for debugging."""
        return f"""
    {self.__class__.__name__}
      start: {self._start}
      current value: {self._value}
      increment_step: {self._increment_step}
      decrement_step: {self._decrement_step}
      min_value: {self._min_value}
      max_value: {self._max_value}
    """


DEFAULT_INT_COUNTER_START: int = 0
DEFAULT_FLOAT_COUNTER_START: float = 0.0
DEFAULT_DECIMAL_COUNTER_START: Decimal = Decimal("0.0")

DEFAULT_INT_STEP_SIZE: int = 1
DEFAULT_FLOAT_STEP_SIZE: float = 1
DEFAULT_DECIMAL_STEP_SIZE: Decimal = Decimal("0.1")


class CounterBuilder:
    @staticmethod
    def count_up_from_zero() -> Counter[int]:
        return Counter[int](
            start=0,
            increment_step=1,
            decrement_step=1,
            min_value=0,
            max_value=cast(int, INFINITY),
        )

    @staticmethod
    def integer_counter_with_defaults(
        start: int = DEFAULT_INT_COUNTER_START,
        increment_step: int = DEFAULT_INT_STEP_SIZE,
        decrement_step: int = DEFAULT_INT_STEP_SIZE,
        min_value: int = cast(int, NEGATIVE_INFINITY),
        max_value: int = cast(int, INFINITY),
        min_value_reached: Callable = do_nothing,
        max_value_reached: Callable = do_nothing,
        increment_action: Callable = do_nothing,
        decrement_action: Callable = do_nothing,
    ) -> Counter[int]:
        return Counter[int](
            start,
            increment_step,
            decrement_step,
            min_value,
            max_value,
            min_value_reached,
            max_value_reached,
            increment_action,
            decrement_action,
        )

    @staticmethod
    def float_counter_with_defaults(
        start: float = DEFAULT_FLOAT_COUNTER_START,
        increment_step: float = DEFAULT_FLOAT_STEP_SIZE,
        decrement_step: float = DEFAULT_FLOAT_STEP_SIZE,
        min_value: float = NEGATIVE_INFINITY,
        max_value: float = INFINITY,
        min_value_reached: Callable = do_nothing,
        max_value_reached: Callable = do_nothing,
        increment_action: Callable = do_nothing,
        decrement_action: Callable = do_nothing,
    ) -> Counter:
        return Counter[float](
            start,
            increment_step,
            decrement_step,
            min_value,
            max_value,
            min_value_reached,
            max_value_reached,
            increment_action,
            decrement_action,
        )

    @staticmethod
    def decimal_counter_with_defaults(
        start: Decimal = DEFAULT_DECIMAL_COUNTER_START,
        increment_step: Decimal = DEFAULT_DECIMAL_STEP_SIZE,
        decrement_step: Decimal = DEFAULT_DECIMAL_STEP_SIZE,
        min_value: Decimal = Decimal("-Infinity"),
        max_value: Decimal = Decimal("Infinity"),
        min_value_reached: Callable = do_nothing,
        max_value_reached: Callable = do_nothing,
        increment_action: Callable = do_nothing,
        decrement_action: Callable = do_nothing,
    ) -> Counter:
        return Counter[Decimal](
            start,
            increment_step,
            decrement_step,
            min_value,
            max_value,
            min_value_reached,
            max_value_reached,
            increment_action,
            decrement_action,
        )
