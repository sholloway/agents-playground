"""
Module of helper functions.
"""

from typing import Any, TypeVar

KeyType = TypeVar("KeyType")
ValueType = TypeVar("ValueType")


def get_or_raise(maybe_something: Any, exception: Exception) -> Any:
    """Handle None checks"""
    if maybe_something is not None:
        return maybe_something
    else:
        raise exception


def map_get_or_raise(
    map: dict[KeyType, ValueType], maybe_key: KeyType, exception: Exception
) -> ValueType:
    if maybe_key in map:
        return map[maybe_key]
    else:
        raise exception
