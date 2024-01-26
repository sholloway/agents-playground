from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce, wraps
import itertools
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

class Coordinate(Generic[CoordinateComponentType], ABC):
  def __init__(self, *components: CoordinateComponentType) -> None:
    self._components = components

  @abstractmethod
  def new(self, *components: CoordinateComponentType) -> Coordinate[CoordinateComponentType]:
    """Create a new matrix with the same shape but with the provided data.""" 
    
  def to_tuple(self) -> Tuple[CoordinateComponentType,...]:
    return tuple(self._components)
  
  def __len__(self) -> int:
    return len(self._components)

  def __getitem__(self, index: int) -> CoordinateComponentType:
    return self._components[index]
  
  @enforce_coordinate_size
  def multiply(self, other: Coordinate) -> Coordinate:
    products = itertools.starmap(operator.mul, zip(self._components, other.to_tuple()))
    return self.new(*products) 
  
  def __mul__(self, other: Coordinate) -> Coordinate:
    return self.multiply(other)

  @enforce_coordinate_size
  def shift(self, other: Coordinate) -> Coordinate:
    sums = itertools.starmap(operator.add, zip(self._components, other.to_tuple()))
    return self.new(*sums) 
  
  def __add__(self, other: Coordinate) -> Coordinate:
    return self.shift(other)
  
  def subtract(self, other: Coordinate) -> Coordinate:
    diffs = itertools.starmap(operator.sub, zip(self._components, other.to_tuple()))
    return self.new(*diffs) 
  
  def __sub__(self, other: Coordinate) -> Coordinate:
    return self.subtract(other)
  
  @enforce_coordinate_size
  def find_distance(self, other: Coordinate) -> float:
    """Finds the Manhattan distance between two locations."""
    differences = itertools.starmap(operator.sub, zip(self._components, other.to_tuple()))
    return reduce(lambda a,b: abs(a) + abs(b), differences)
  
class Coordinate2d(Coordinate):
  def __init__(self, x:CoordinateComponentType, y: CoordinateComponentType ) -> None:
    super().__init__(x, y)

  @property
  def x(self) -> CoordinateComponentType:
    return self._components[0]
  
  @property
  def y(self) -> CoordinateComponentType:
    return self._components[1]

  def new(self, *components: CoordinateComponentType) -> Coordinate[CoordinateComponentType]:
    if len(components) != 2:
      raise CoordinateError(f'Coordinate2d.new can only be called with two components. {len(components)} was provided.')
    return Coordinate2d(components[0], components[1])
  
class Coordinate3d(Coordinate):
  def __init__(self, x:CoordinateComponentType, y: CoordinateComponentType, z: CoordinateComponentType) -> None:
    super().__init__(x, y, z)

  @property
  def x(self) -> CoordinateComponentType:
    return self._components[0]
  
  @property
  def y(self) -> CoordinateComponentType:
    return self._components[1]
  
  @property
  def z(self) -> CoordinateComponentType:
    return self._components[2]
  
  def new(self, *components: CoordinateComponentType) -> Coordinate[CoordinateComponentType]:
    if len(components) != 3:
      raise CoordinateError(f'Coordinate3d.new can only be called with three components. {len(components)} was provided.')
    return Coordinate3d(components[0], components[1], components[2])