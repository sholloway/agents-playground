"""
Module for defining types used by the core classes.
"""

from __future__ import annotations
from dataclasses import dataclass

from decimal import Decimal
from fractions import Fraction
from functools import wraps
from typing import Generic, List, Tuple, TypeVar

# Time based Types
TimeInSecs = float
TimeInMS = float

# Units of Measure
MegaBytes = float
Percentage = float
Count = int

# Performance Related
Sample = int | float

# Coordinates
# Note the definition of CanvasLocation is driven by DPGs annoying
# habit of inconsistent return types.
CanvasLocation = List[int] | Tuple[int, ...]
CellLocation = Tuple[int, int]

# Handling Size
NumericTypeAlias = int | float | Fraction | Decimal
NumericType = TypeVar("NumericType", int, float, Fraction, Decimal)


class NumericTypeError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def box_numeric_value(value, original) -> NumericTypeAlias:
    original_type = type(original)
    match original_type.__name__:
        case "int" | "float":
            return float(value)
        case "Decimal":
            return Decimal(str(value))
        case "Fraction":
            return Fraction(value)
        case _:
            raise Exception("Unsupported type.")


def enforce_same_type(func):
    """
    A decorator that forces all parameters to have the same type.

    Note: This is intended to be used on instance methods. 
    So the first parameter is expected to be the instance of the 
    class (i.e. "self"). With that convention, the type of the 
    second parameter is determined and then used to check against
    the remaining types.
    """

    @wraps(func)
    def _guard(*args, **kwargs):
        first = args[1] # Skip "self" on the instance method.
        others = args[2:]

        expected_type = type(first)
        for value in others:
            if type(value) != expected_type:
                error_msg = "Cannot mix parameter types."
                raise NumericTypeError(error_msg)

        return func(*args, **kwargs)

    return _guard


@dataclass(init=False)
class Size(Generic[NumericType]):
    width: NumericType
    height: NumericType

    def __init__(self, w: NumericType, h: NumericType) -> None:
        self.width = w
        self.height = h

    def scale(self, amount: NumericType) -> Size[NumericType]:
        return Size(self.width * amount, self.height * amount)
