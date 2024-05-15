from __future__ import print_function

from collections import deque
import functools
from itertools import chain
from sys import getsizeof, stderr
import time
from typing import Any

try:
    from reprlib import repr
except ImportError:
    pass

from agents_playground.sys.logger import get_default_logger


def _profile(func, *args, **kwargs):
    logger = get_default_logger()
    try:
        start_time_s = time.perf_counter()
        # Actually run the decorated function.
        result = func(*args, **kwargs)
        end_time_s = time.perf_counter()
        duration_s = end_time_s - start_time_s
        logger.debug(
            f"{func.__name__} runtime {duration_s} seconds | {duration_s * 1000} ms"
        )
        return result
    except Exception as e:
        logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
        raise e


def _pass_through(func, *args, **kwargs):
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
    size_in_bytes = getsizeof(object)
    logger.debug(f"{label}'s size: {size_in_bytes} bytes")


# From the online recipe: https://code.activestate.com/recipes/577504/
def total_size(o, handlers={}):
    """Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    Args
      - o: The container object to find the size of.
      - handlers: A dictionary in which you can register additional handlers.
    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {
        tuple: iter,
        list: iter,
        deque: iter,
        dict: dict_handler,
        set: iter,
        frozenset: iter,
    }
    all_handlers.update(handlers)  # user handlers take precedence
    seen = set()  # track which object id's have already been seen
    default_size = getsizeof(0)  # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:  # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)
