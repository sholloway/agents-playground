from typing import Union
from math import inf as INFINITY
NEGATIVE_INFINITY = -INFINITY

class Counter:
  def __init__(self, 
    start: Union[int, float]=0, 
    increment_step: Union[int, float]=1, 
    decrement_step: Union[int, float]=1,
    min_value: Union[int, float] = NEGATIVE_INFINITY,
    max_value: Union[int, float] = INFINITY
  ):
    self._start = start
    self._value: Union[int, float] = start
    self._increment_step: Union[int, float] = increment_step
    self._decrement_step: Union[int, float] = decrement_step
    self._min_value: Union[int, float] = min_value
    self._max_value: Union[int, float] = max_value

  def increment(self) -> Union[int, float]:
    if self._value < self._max_value:
      self._value += self._increment_step
    return self._value

  def decrement(self) -> Union[int, float]:
    if self._value > self._min_value:
      self._value -= self._decrement_step
    return self._value

  def value(self) -> Union[int, float]:
    return self._value

  def reset(self):
    self._value = self._start

  def at_min_value(self) -> bool:
    return self._value == self._min_value

  def at_max_value(self) -> bool:
    return self._value == self._max_value