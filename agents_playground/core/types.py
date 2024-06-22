"""
Module for defining types used by the core classes.
"""

from __future__ import annotations
from dataclasses import dataclass

from decimal import Decimal
from fractions import Fraction
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

def box_numeric_value(value, original) -> NumericTypeAlias:
    original_type = type(original)
    match original_type.__name__:
        case 'int':
            return int(value)
        case 'float':
            return float(value)
        case 'Decimal':
            return Decimal(str(value))
        case 'Fraction':
            return Fraction(value)
        case _:
            raise Exception('Unsupported type.')
        
@dataclass(init=False)
class Size(Generic[NumericType]):
    width: NumericType
    height: NumericType

    def __init__(self, w: NumericType, h: NumericType) -> None:
        self.width = w
        self.height = h

    def scale(self, amount: NumericType) -> Size[NumericType]:
        return Size(self.width * amount, self.height * amount)

