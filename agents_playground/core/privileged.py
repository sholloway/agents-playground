"""
Module that provides functions for working with access rights.
"""

from functools import wraps
import os
from typing import Any, Callable


def running_as_root() -> bool:
    """Determine if the process is running as root."""
    return os.geteuid() == 0


def require_root(func) -> Callable:
    """Only call the decorated function if the effective user is root."""

    @wraps(func)
    def wrapper(*args, **kargs) -> Any:
        result = None
        if running_as_root():
            result = func(*args, **kargs)
        return result

    return wrapper
