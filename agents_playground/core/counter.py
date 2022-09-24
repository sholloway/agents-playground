from typing import Callable, Union
from math import inf as INFINITY
NEGATIVE_INFINITY = -INFINITY

class Counter:
  """
  A smart counter. Can be used to count up or down. 

  Args:
    - start: The value to start the counter at.
    - increment_step: The size of step to count up.
    - decrement_step: The size of step to count down.
    - min_value: The lowest value (inclusive) the counter can count down to.
    - max_value: The highest value (inclusive) the counter can count up to.
    - min_value_reached: An optional callable to invoke when the minimum value is reached.
    - max_value_reached: An optional callable to invoke when the maximum value is reached.
  """
  def __init__(self, 
    start: Union[int, float]=0, 
    increment_step: Union[int, float]=1, 
    decrement_step: Union[int, float]=1,
    min_value: Union[int, float] = NEGATIVE_INFINITY,
    max_value: Union[int, float] = INFINITY,
    min_value_reached: Callable = None,
    max_value_reached: Callable = None
  ):
    self.__start = start
    self.__value: Union[int, float] = start
    self.__increment_step: Union[int, float] = increment_step
    self.__decrement_step: Union[int, float] = decrement_step
    self.__min_value: Union[int, float] = min_value
    self.__max_value: Union[int, float] = max_value
    self.__min_value_reached = min_value_reached
    self.__max_value_reached = max_value_reached

  def increment(self) -> Union[int, float]:
    if self.__value < self.__max_value:
      self.__value += self.__increment_step
    else:
      if self.__max_value_reached != None:
        self.__max_value_reached()
    return self.__value

  def decrement(self) -> Union[int, float]:
    if self.__value > self.__min_value:
      self.__value -= self.__decrement_step
    else:
      if self.__min_value_reached != None:
        self.__min_value_reached()
    return self.__value

  def value(self) -> Union[int, float]:
    return self.__value

  def reset(self):
    self.__value = self.__start

  def at_min_value(self) -> bool:
    return self.__value == self.__min_value

  def at_max_value(self) -> bool:
    return self.__value == self.__max_value

  def __repr__(self) -> str:
    return f"""
    agents_playground.core.counter.Counter object
      start: {self.__start} 
      current value: {self.__value}
      increment_step: {self.__increment_step}
      decrement_step: {self.__decrement_step}
      min_value: {self.__min_value}
      max_value: {self.__max_value}
    """