from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from functools import reduce, wraps
import itertools
import math
import operator

# Convenience tuples for working with grid coordinates.
from typing import Generic, Iterator

from agents_playground.core.types import NumericType
SPATIAL_ROUNDING_PRECISION: int = 8

def f(numerator: NumericType, denominator: int=1) -> Fraction:
    """Creates a new fraction."""
    if denominator == 1:
        # If no denominator is provided then we're probably converting
        # an int, float, or decimal to a fraction
        return Fraction(numerator)
    else:
        # Otherwise, we're trying to construct a fraction from a 
        # numerator and denominator. 
        return Fraction(int(numerator), denominator)

def d(value) -> Decimal:
    """Creates a decimal."""
    return Decimal(value)

class CoordinateError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def enforce_coordinate_size(func):
    """A decorator that guards against using another coordinate of a different size."""

    @wraps(func)
    def _guard(*args, **kwargs):
        self: Coordinate = args[0]
        other: Coordinate = args[1]
        if len(self) == len(other):
            return func(*args, **kwargs)
        else:
            error_msg = f"Cannot perform this operation on coordinates that are of different sizes."
            raise CoordinateError(error_msg)

    return _guard

def enforce_coordinate_type(func):
    """A decorator that guards against using another coordinate of a different type.
    Prevents mixing integers, floats, and fractions. 
    """

    @wraps(func)
    def _guard(*args, **kwargs):
        self: Coordinate = args[0]
        other: Coordinate = args[1]
        
        # Look at the first type in this coordinate. If any of the types are different
        # raise an error.
        expected_type = type(self[0])
        for value in itertools.chain(self, other):
            if type(value) != expected_type:
                error_msg = (
                    "Cannot mix coordinates of different types.",
                    f"Attempted to mix {expected_type.__name__} with {type(value).__name__}"
                )
                raise CoordinateError(error_msg)
        
        return func(*args, **kwargs)
    return _guard

class Coordinate(Generic[NumericType]):
    """
    A coordinate represents a location in a coordinate space.
    It can be of any number of dimensions (e.g. 1D, 2D, 3D,...ND)
    """

    def __init__(self, *components: NumericType) -> None:
        self._components: tuple[NumericType,...] = components

    def dimensions(self) -> int:
        """Returns the number of dimensions the coordinate is in."""
        return len(self._components)

    def to_tuple(self) -> tuple[NumericType, ...]:
        return tuple(self._components)

    def __len__(self) -> int:
        return len(self._components)

    def __getitem__(self:Coordinate[NumericType], lookup: int) -> NumericType:
        return self._components[lookup]
        
    @enforce_coordinate_type
    @enforce_coordinate_size
    def __eq__(self: Coordinate[NumericType], other: Coordinate[NumericType]) -> bool:
        close: Iterator[bool] = itertools.starmap(math.isclose, zip(self._components, other.to_tuple()))
        return all(close)

    def __repr__(self) -> str:
        return f"Coordinate{self._components}"

    def __hash__(self) -> int:
        return self._components.__hash__()

    @enforce_coordinate_type
    @enforce_coordinate_size
    def multiply(self: Coordinate[NumericType], other: Coordinate[NumericType]) -> Coordinate[NumericType]:
        products = itertools.starmap(
            operator.mul, zip(self._components, other.to_tuple())
        )
        return Coordinate(*products)

    def __mul__(self: Coordinate[NumericType], other: Coordinate[NumericType]) -> Coordinate[NumericType]:
        return self.multiply(other)

    @enforce_coordinate_type
    @enforce_coordinate_size
    def shift(self: Coordinate[NumericType], other: Coordinate[NumericType]) -> Coordinate[NumericType]:
        sums = itertools.starmap(operator.add, zip(self._components, other.to_tuple()))
        return Coordinate(*sums)

    def add(self: Coordinate[NumericType], other: Coordinate[NumericType]) -> Coordinate[NumericType]:
        return self.shift(other)

    def __add__(self: Coordinate[NumericType], other: Coordinate[NumericType]) -> Coordinate[NumericType]:
        return self.shift(other)

    @enforce_coordinate_type
    @enforce_coordinate_size
    def subtract(self: Coordinate[NumericType], other: Coordinate[NumericType]) -> Coordinate[NumericType]:
        diffs = itertools.starmap(operator.sub, zip(self._components, other.to_tuple()))
        return Coordinate(*diffs)

    def __sub__(self:Coordinate[NumericType], other: Coordinate[NumericType]) -> Coordinate[NumericType]:
        return self.subtract(other)

    @enforce_coordinate_type
    @enforce_coordinate_size
    def find_manhattan_distance(self: Coordinate[NumericType], other: Coordinate[NumericType]) -> float | Fraction:
        """Finds the Manhattan distance between two locations."""
        differences = itertools.starmap(
            operator.sub, zip(self._components, other.to_tuple())
        )
        return reduce(lambda a, b: abs(a) + abs(b), differences)

    @enforce_coordinate_type
    @enforce_coordinate_size
    def find_euclidean_distance(self: Coordinate[NumericType], other: Coordinate[NumericType]) -> float | Fraction:
        """Finds the Euclidean distance (as the crow flies) between two locations."""
        differences = itertools.starmap(
            operator.sub, zip(self._components, other.to_tuple())
        )
        squared_differences = list(map(lambda i: i * i, differences))
        summation = reduce(operator.add, squared_differences)
        distance = math.sqrt(summation)
        if isinstance(self[0], Fraction):
            return Fraction(distance)
        else:
            return distance
    
    def __iter__(self: Coordinate[NumericType]) -> Iterator[NumericType]:
        return iter(self._components)
    
    def to_ints(self: Coordinate[NumericType]) -> Coordinate[int]:
        """
        Returns the coordinate as a coordinate composed of integers.
        Note that this can result in a loss of precision.
        """
        return Coordinate(*map(int, self._components))
    
    def to_floats(self: Coordinate[NumericType]) -> Coordinate[float]:
        """
        Returns the coordinate as a coordinate composed of floats.
        Note that this can result in a loss of precision.
        """
        return Coordinate(*map(float, self._components))
    
    def to_fractions(self: Coordinate[NumericType]) -> Coordinate[Fraction]:
        """
        Returns the coordinate as a coordinate composed of fractions.
        Note that this can result in a loss of precision.
        """
        return Coordinate(*map(f, self._components))
    
    def to_decimals(self: Coordinate[NumericType]) -> Coordinate[Decimal]:
        """
        Returns the coordinate as a coordinate composed of fractions.
        Note that this can result in a loss of precision. Converting from 
        fractions to decimals is handled internally by first converting to floats.
        """
        current_type = type(self._components[0])
        if current_type.__name__  == 'Fraction':
            return self.to_floats().to_decimals()
        else:
            return Coordinate(*map(d, self._components))
