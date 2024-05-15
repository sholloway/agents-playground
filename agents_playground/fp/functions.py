"""
This module is a collection of helper functions for the common
tasks in functional programming.
"""

from functools import partial, reduce, wraps
from inspect import signature
from typing import Any, Callable


def identity(value: Any) -> Any:
    """Identify function."""
    return value


def curry(func):
    """A decorator that turns a normal function into a curried function.

    Example
    @curry
    def add(a,b,c)
      return a+b+b

    Enables calling it as:
    add(1)(2)(3)
    """

    @wraps(func)
    def _curry(param):
        if len(signature(func).parameters) == 1:
            return func(param)
        return curry(partial(func, param))

    return _curry


def compose(*functions: Callable) -> Callable:
    """
    Utility function that enables composing functions as
    a(b(c())) by calling compose(a,b,c)

    Example
    do_stuff = compose(step_1, step_2, step_3)
    do_stuff() == step_1(step_2(step_3))
    """

    def _apply(f, g):
        return lambda x=None: f(g(x))

    return reduce(_apply, functions, identity)


def chain(*functions: Callable) -> Callable:
    """Orchestrate a series of functions.
    Given a chain(a,b,c),
    orchestrates a() -> b(output of a) -> c(output of b)
    """

    def _chain(input):
        accumulate_result = input
        for func in functions:
            accumulate_result = func(accumulate_result)
        return accumulate_result

    return _chain
