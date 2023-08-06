from __future__ import annotations
from abc import ABC, abstractmethod

from . import *

"""
What do I need in an FP framework?
- Smooth way to deal with errors.
- Enable easy encapsulation of ADTs.

Building Blocks
- Functor
- Monoid
- Monad
- Applicative
- Alternative
- Foldable
- Traversable
- NFData
- Typeable
- Generic

Useful Classes
- Just
- Either
  - Left
  - Right
- Maybe
  - Some
  - Nothing
- Result
  - Success
  - Failure

Functional Tools
- identity
- curry
- compose
- chain/pipe
- map
- bind/fmap
- fold
"""



from typing import Any, Callable, cast, Generic, Protocol, TypeVar

MaybeValue = TypeVar('MaybeValue')
A = TypeVar('A', covariant=True)
B = TypeVar('B', covariant=True)

"""Identify function."""
def identity(value: Any) -> Any:
  return value

class Functor(Protocol[A]):
  """
  A functor is a design pattern that enables applying functions 
  to a value inside of a generic type without changing the 
  structure of the generic type.

  A functor has the following properties.

  It is an effect type (i.e. a generic type).
  It has a map function that applies a function to the effects world.
  It adheres to the Functor Laws which ensures that the map 
  function does not change the structure of the container only the
  elements. Simply put, map changes a value without altering it’s context.
  """
  def map(self, func: Callable[[A], B]) -> Functor[B]:
    ...

class Monad(Protocol):
  ...

class Applicative(Protocol):
  ...

class Unwrappable(Protocol[A]):
  """An unwrappable has the ability to export the internal wrapped value."""
  def unwrap(self) -> A:
    ...

class UnwrappedException(Exception):
  """
  An exception for when unwrapped was called in a context that 
  isn't appropriate.
  """
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class Just(Unwrappable, Generic[A]):
  def __init__(self, value: A) -> None:
    super().__init__()
    self._value = value 

  def unwrap(self) -> A:
    return self._value
  
  def __eq__(self, other: object) -> bool:
    if hasattr(other, 'unwrap'):
      return self._value.__eq__(cast(Unwrappable,other).unwrap())
    else:
      return self._value.__eq__(other)
  

class Maybe(Unwrappable, Functor, Protocol[MaybeValue]):
  @staticmethod
  def from_value(value: MaybeValue) -> 'Maybe[MaybeValue]':
    return Something(value)
  

class Nothing(Maybe[Any]):
  def __init__(self, value: None = None) -> None:
    super().__init__()
    self._value = value

  def unwrap(self) -> Any:
    return None
  
  def map(self, func: Callable[[Any], B]) -> Functor[B]:
    """Map doesn't do anything on Nothing."""
    return self


class Something(Maybe[MaybeValue]):
  def __init__(self, value: MaybeValue) -> None:
    super().__init__()
    self._value = value

  def unwrap(self) -> MaybeValue:
    return self._value

  def map(self, func: Callable[[MaybeValue], B]) -> Functor[B]:
    return Something(func(self.unwrap()))