from typing import Callable, Optional, Union
from math import inf as INFINITY
NEGATIVE_INFINITY = -INFINITY

DEFAULT_COUNTER_START: int = 0
DEFAULT_STEP_SIZE: int = 1

def do_nothing(**kargs) -> None:
  """A pass through function used to simplify the Counter defaults."""
  pass

class Counter:
  """ An actionable counter. 
  Can be used to count up or down and optionally take action when targets are reached.
  """

  def __init__(self, 
    start: int | float = DEFAULT_COUNTER_START, 
    increment_step: int | float = DEFAULT_STEP_SIZE, 
    decrement_step: int | float = DEFAULT_STEP_SIZE,
    min_value: int | float = NEGATIVE_INFINITY,
    max_value: int | float = INFINITY,
    min_value_reached: Callable = do_nothing,
    max_value_reached: Callable = do_nothing,
    increment_action:  Callable = do_nothing,
    decrement_action:  Callable = do_nothing
  ) -> None:
    """
    An actionable counter. Can be used to count up or down and optional take action
    when targets are reached.

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
    self._start = start
    self._value: int | float = start
    self._increment_step: int | float = increment_step
    self._decrement_step: int | float = decrement_step
    self._min_value: int | float = min_value
    self._max_value: int | float = max_value

    self._min_value_reached: Callable = min_value_reached
    self._max_value_reached: Callable = max_value_reached
    self._increment_action: Callable  = increment_action
    self._decrement_action: Callable  = decrement_action

  def increment(self, **kargs) -> int | float:
    """Counts up by the step amount.
    
    Args:
      - kargs: Named parameters that can be passed to the increment_action and 
        max_value_reached action.

    Returns:
      The new value the counter is at.
    """
    if self._value < self._max_value:
      self._value += self._increment_step
      self._increment_action(**kargs)
    else:
      self._max_value_reached(**kargs)
    return self._value

  def decrement(self, **kargs) -> int | float:
    """Counts down by the step amount.
    
    Args:
      - kargs: Named parameters that can be passed to the decrement_action and 
        min_value_reached action.

    Returns:
      The new value the counter is at.
    """
    if self._value > self._min_value:
      self._value -= self._decrement_step
      self._decrement_action(**kargs)
    else:
      self._min_value_reached(**kargs)
    return self._value

  def value(self) -> int | float:
    """A getter function for the counter's current value."""
    return self._value

  def set(self, value: int | float) -> None:
    """Set the active value."""
    self._value = value

  def reset(self) -> None:
    """Resets the counter to the start value."""
    self._value = self._start

  def at_min_value(self) -> bool:
    """Determines if the counter is at the lower threshold."""
    return self._value == self._min_value

  def at_max_value(self) -> bool:
    """Determines if the counter is at the upper threshold."""
    return self._value == self._max_value

  def __repr__(self) -> str:
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