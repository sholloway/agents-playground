"""
Module for defining types used by the core classes.
"""

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
import enum 
from fractions import Fraction
from functools import wraps
from typing import Any, Callable, Generic, List, Tuple, TypeVar

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

def identify_type(value):
    """
    Finds the type of an instance. Unwraps enums.
    """
    value_type = type(value)
    if isinstance(value_type, enum.EnumType):
        # The value is an enum. Return the type of the enum's value.
        return type(value.value)
    else:
        return value_type
        
def init_must_be_homogeneous(func: Callable[[Any], None]) -> Callable:
    """
    A decorator that forces all parameters to have the same type.

    Note: This is intended to be used on __init__ methods and has
    the following behavior.
    1. The first parameter is expected to be the instance of the 
    class (i.e. "self"). With that convention, the type of the 
    second parameter is determined and then used to check against
    the remaining types.
    
    2. The called function (__init__) does not return anything.
    """
    @wraps(func)
    def _guard(*args, **kwargs) -> None:
        first = args[1] # Skip the first arg since it is the instance's "self".
        others = args[2:]
        expected_type = identify_type(first)
        for value in others:
            if identify_type(value) != expected_type:
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
