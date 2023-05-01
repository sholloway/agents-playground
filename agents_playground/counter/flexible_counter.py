"""
What are my options here:
- Generics: Not going to work well because int, float cannot be compared to decimal.
- Delegation
- Protocol
- Abstract Class
"""


from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Callable, Generic, Protocol, TypeVar

from math import inf as INFINITY
NEGATIVE_INFINITY = -INFINITY

DEFAULT_COUNTER_START: int = 0
DEFAULT_STEP_SIZE: int = 1

def do_nothing(**_) -> None:
  """A pass through function used to simplify the Counter defaults."""
  pass

PrecisionType = TypeVar('PrecisionType', int, float, Decimal)


class FlexibleCounter(ABC, Generic[PrecisionType]):
  @abstractmethod
  def increment(self, **kwargs) -> PrecisionType:
    ...
  
  @abstractmethod
  def decrement(self, **kwargs) -> PrecisionType:
    ...

  @abstractmethod
  def value(self) -> PrecisionType:
    ...

  @abstractmethod
  def set(self, value: PrecisionType) -> None:
    ...

  @abstractmethod
  def reset(self) -> None:
    ...

  @abstractmethod
  def at_min_value(self) -> bool:
    ...

  @abstractmethod
  def at_max_value(self) -> bool:
    ...

class IntCounter(FlexibleCounter, int):
  def __init__(
    self, 
    start: int                  = DEFAULT_COUNTER_START, 
    increment_step: int         = DEFAULT_STEP_SIZE, 
    decrement_step: int         = DEFAULT_STEP_SIZE,
    min_value: int | float      = NEGATIVE_INFINITY,
    max_value: int | float      = INFINITY,
    min_value_reached: Callable = do_nothing,
    max_value_reached: Callable = do_nothing,
    increment_action:  Callable = do_nothing,
    decrement_action:  Callable = do_nothing
  ) -> None:
    super().__init__()
    self._start = start
    self._value = start
    self._increment_step = increment_step
    self._decrement_step = decrement_step
    self._min_value      = min_value
    self._max_value      = max_value

    self._min_value_reached = min_value_reached
    self._max_value_reached = max_value_reached
    self._increment_action  = increment_action
    self._decrement_action  = decrement_action

  def increment(self, **kwargs) -> int:
    """Counts up by the step amount.
    
    Args:
      - kwargs: Named parameters that can be passed to the increment_action and 
        max_value_reached action.

    Returns:
      The new value the counter is at.
    """
    if self._value < self._max_value:
      self._value += self._increment_step
      self._increment_action(**kwargs)
    else:
      self._max_value_reached(**kwargs)
    return self._value
  
  def decrement(self, **kwargs) -> int:
    """Counts down by the step amount.
    
    Args:
      - kwargs: Named parameters that can be passed to the decrement_action and 
        min_value_reached action.

    Returns:
      The new value the counter is at.
    """
    if self._value > self._min_value:
      self._value -= self._decrement_step
      self._decrement_action(**kwargs)
    else:
      self._min_value_reached(**kwargs)
    return self._value
  
  def value(self) -> int:
    """A getter function for the counter's current value."""
    return self._value
  
  def set(self, value: int) -> None:
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

class FloatCounter(FlexibleCounter, float):
  def __init__(
    self, 
    start: float                  = DEFAULT_COUNTER_START, 
    increment_step: float         = DEFAULT_STEP_SIZE, 
    decrement_step: float         = DEFAULT_STEP_SIZE,
    min_value: float              = NEGATIVE_INFINITY,
    max_value: float              = INFINITY,
    min_value_reached: Callable = do_nothing,
    max_value_reached: Callable = do_nothing,
    increment_action:  Callable = do_nothing,
    decrement_action:  Callable = do_nothing
  ) -> None:
    super().__init__()
    self._start = start
    self._value = start
    self._increment_step = increment_step
    self._decrement_step = decrement_step
    self._min_value      = min_value
    self._max_value      = max_value

    self._min_value_reached = min_value_reached
    self._max_value_reached = max_value_reached
    self._increment_action  = increment_action
    self._decrement_action  = decrement_action

  def increment(self, **kwargs) -> float:
    """Counts up by the step amount.
    
    Args:
      - kwargs: Named parameters that can be passed to the increment_action and 
        max_value_reached action.

    Returns:
      The new value the counter is at.
    """
    if self._value < self._max_value:
      self._value += self._increment_step
      self._increment_action(**kwargs)
    else:
      self._max_value_reached(**kwargs)
    return self._value
  
  def decrement(self, **kwargs) -> float:
    """Counts down by the step amount.
    
    Args:
      - kwargs: Named parameters that can be passed to the decrement_action and 
        min_value_reached action.

    Returns:
      The new value the counter is at.
    """
    if self._value > self._min_value:
      self._value -= self._decrement_step
      self._decrement_action(**kwargs)
    else:
      self._min_value_reached(**kwargs)
    return self._value
  
  def value(self) -> float:
    """A getter function for the counter's current value."""
    return self._value
  
  def set(self, value: float) -> None:
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
  
