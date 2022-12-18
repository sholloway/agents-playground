import time
from typing import Any, List

from agents_playground.terminal.callable import Callable
from agents_playground.terminal.interpreter import Interpreter

class ClockCallable(Callable):
  def arity(self) -> int:
    return 0;

  def call(self, interpreter: Interpreter, args: List[Any]) -> float:
    """Returns the current time in fractional seconds. Intended for benchmarking."""
    return time.perf_counter()

  def __str__(self) -> str:
    return '<function clock>'