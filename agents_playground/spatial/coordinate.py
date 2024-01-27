from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce, wraps
import itertools
import math
import operator

# Convenience tuples for working with grid coordinates.
from typing import Generic, NamedTuple, Protocol, Tuple, TypeVar
from typing_extensions import SupportsIndex

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

CoordinateComponentType = TypeVar('CoordinateComponentType', int, float)

class Coordinate(Generic[CoordinateComponentType]):
  """
  A coordinate represents a location in a coordinate space. 
  It can be of any number of dimensions (e.g. 1D, 2D, 3D,...ND)
  """
  def __init__(self, *components: CoordinateComponentType) -> None:
    self._components = components
  
  def to_tuple(self) -> Tuple[CoordinateComponentType,...]:
    return tuple(self._components)
  
  def __len__(self) -> int:
    return len(self._components)

  def __getitem__(self, index: int) -> CoordinateComponentType:
    return self._components[index]
  
  @enforce_coordinate_size
  def multiply(self, other: Coordinate) -> Coordinate:
    products = itertools.starmap(operator.mul, zip(self._components, other.to_tuple()))
    return Coordinate(*products) 
  
  def __mul__(self, other: Coordinate) -> Coordinate:
    return self.multiply(other)

  @enforce_coordinate_size
  def shift(self, other: Coordinate) -> Coordinate:
    sums = itertools.starmap(operator.add, zip(self._components, other.to_tuple()))
    return Coordinate(*sums) 
  
  def add(self, other: Coordinate) -> Coordinate:
    return self.shift(other)
  
  def __add__(self, other: Coordinate) -> Coordinate:
    return self.shift(other)
  
  @enforce_coordinate_size
  def subtract(self, other: Coordinate) -> Coordinate:
    diffs = itertools.starmap(operator.sub, zip(self._components, other.to_tuple()))
    return Coordinate(*diffs) 
  
  def __sub__(self, other: Coordinate) -> Coordinate:
    return self.subtract(other)
  
  @enforce_coordinate_size
  def find_manhattan_distance(self, other: Coordinate) -> float:
    """Finds the Manhattan distance between two locations."""
    differences = itertools.starmap(operator.sub, zip(self._components, other.to_tuple()))
    return reduce(lambda a,b: abs(a) + abs(b), differences)
  
  @enforce_coordinate_size
  def find_euclidean_distance(self, other: Coordinate) -> float:
    """Finds the Euclidean distance (as the crow flies) between two locations."""
    differences = itertools.starmap(operator.sub, zip(self._components, other.to_tuple()))
    squared_differences = list(map(lambda i: i*i, differences))
    summation = reduce(operator.add, squared_differences)
    return math.sqrt(summation)