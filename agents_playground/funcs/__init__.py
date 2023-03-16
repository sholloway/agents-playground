"""
Module of helper functions.
"""

from typing import Any


def get_or_raise(maybe_something: Any, exception: Exception) -> Any:
  """Handle None checks"""
  if maybe_something is not None:
    return maybe_something 
  else:
    raise exception

def map_get_or_raise(map: dict, maybe_key: Any, exception: Exception) -> Any:
  if maybe_key in map:
    return map[maybe_key] 
  else:
    raise exception