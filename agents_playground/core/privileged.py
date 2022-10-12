"""
Module that provides functions for working with access rights.
"""

from functools import wraps
import os
from typing import Any, Callable

def require_root(func) -> Callable:
  """ Only call the decorated function if the effective user is root."""
  @wraps(func)
  def wrapper(*args, **kargs) -> Any:
    result = None
    if os.geteuid() == 0:
      result = func(*args, **kargs)
    return result
  return wrapper
  
