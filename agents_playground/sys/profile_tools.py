import functools
import sys
import time
from typing import Any

from agents_playground.sys.logger import get_default_logger

def _profile(func,*args, **kwargs):
  logger = get_default_logger()
  try:
    start_time_s = time.perf_counter()
    # Actually run the decorated function.
    result = func(*args, **kwargs)
    end_time_s  = time.perf_counter()
    duration_s = end_time_s - start_time_s
    logger.debug(f'{func.__name__} runtime {duration_s} seconds | {duration_s * 1000} ms')
    return result
  except Exception as e:
    logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
    raise e

def _pass_through(func,*args, **kwargs):
  result = func(*args, **kwargs)
  return result

def timer(func):
  """
  A timer decorator. Logs the time spent in a function at the DEBUG level.
  Only runs if __debug__ is true.
  This is controlled on the command line:
  python -X dev ...

  Example:
  @timer
  some_function()
  """
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    if __debug__:
      _profile(func, *args, **kwargs)
    else:
      _pass_through(func, *args, **kwargs)
  return wrapper

  
def size(label: str, object: Any) -> None:
  """
  Logs the size of an object.

  Parameters
  label: Provide the name of the object.
  """
  logger = get_default_logger()
  size_in_bytes = sys.getsizeof(object)
  logger.debug(f'{label}\'s size: {size_in_bytes} bytes')