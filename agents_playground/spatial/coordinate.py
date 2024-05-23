from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from fractions import Fraction
from functools import reduce, wraps
import itertools
import math
import operator

# Convenience tuples for working with grid coordinates.
from typing import Generic, Iterator, NamedTuple, Protocol, Tuple, TypeVar
from typing_extensions import SupportsIndex
SPATIAL_ROUNDING_PRECISION: int = 8

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
                error_msg = "Cannot mix coordinates of different types."
                raise CoordinateError(error_msg)
        
        return func(*args, **kwargs)
    return _guard



CoordinateComponentType = TypeVar("CoordinateComponentType", int, float, Fraction)

class Coordinate(Generic[CoordinateComponentType]):
    """
    A coordinate represents a location in a coordinate space.
    It can be of any number of dimensions (e.g. 1D, 2D, 3D,...ND)
    """

    def __init__(self, *components: CoordinateComponentType) -> None:
        self._components = components

    def dimensions(self) -> int:
        """Returns the number of dimensions the coordinate is in."""
        return len(self._components)

    def to_tuple(self) -> Tuple[CoordinateComponentType, ...]:
        return tuple(self._components)

    def __len__(self) -> int:
        return len(self._components)

    def __getitem__(self, lookup: int | slice) -> CoordinateComponentType | Coordinate:
        if isinstance(lookup, int):
            return self._components[lookup]
        elif isinstance(lookup, slice):
            return Coordinate(*self._components[lookup])

    def __eq__(self, other: Coordinate) -> bool:
        return self.to_tuple().__eq__(other.to_tuple())

    def __repr__(self) -> str:
        return f"Coordinate{self._components}"

    def __hash__(self) -> int:
        return self._components.__hash__()

    @enforce_coordinate_type
    @enforce_coordinate_size
    def multiply(self, other: Coordinate) -> Coordinate:
        products = itertools.starmap(
            operator.mul, zip(self._components, other.to_tuple())
        )
        return Coordinate(*products)

    def __mul__(self, other: Coordinate) -> Coordinate:
        return self.multiply(other)

    @enforce_coordinate_type
    @enforce_coordinate_size
    def shift(self, other: Coordinate) -> Coordinate:
        sums = itertools.starmap(operator.add, zip(self._components, other.to_tuple()))
        return Coordinate(*sums)

    def add(self, other: Coordinate) -> Coordinate:
        return self.shift(other)

    def __add__(self, other: Coordinate) -> Coordinate:
        return self.shift(other)

    @enforce_coordinate_type
    @enforce_coordinate_size
    def subtract(self, other: Coordinate) -> Coordinate:
        diffs = itertools.starmap(operator.sub, zip(self._components, other.to_tuple()))
        return Coordinate(*diffs)

    def __sub__(self, other: Coordinate) -> Coordinate:
        return self.subtract(other)

    @enforce_coordinate_type
    @enforce_coordinate_size
    def find_manhattan_distance(self, other: Coordinate) -> float | Fraction:
        """Finds the Manhattan distance between two locations."""
        differences = itertools.starmap(
            operator.sub, zip(self._components, other.to_tuple())
        )
        return reduce(lambda a, b: abs(a) + abs(b), differences)

    @enforce_coordinate_type
    @enforce_coordinate_size
    def find_euclidean_distance(self, other: Coordinate) -> float | Fraction:
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
    
    def __iter__(self) -> Iterator:
        return iter(self._components)
