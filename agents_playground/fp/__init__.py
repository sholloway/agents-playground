from __future__ import annotations

from collections.abc import Collection, Hashable
from enum import Enum, auto

from . import *

"""
What do I need in an FP framework?
- Smooth way to deal with errors. (Either)
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

Functional Tools
- identity
- curry
- compose
- chain/pipe

- map
- bind/fmap
- fold
"""

from typing import (
  Any, 
  Callable,
  cast, 
  Generic, 
  Protocol, 
  TypeVar
)

A = TypeVar('A', covariant=True)
B = TypeVar('B', covariant=True)

WrappableValue = TypeVar('WrappableValue')
class Wrappable(Protocol[WrappableValue]):
  """An unwrappable has the ability to export the internal wrapped value."""
  def wrap(self, value: WrappableValue) -> 'Wrappable[WrappableValue]':
    """Takes a value and wraps it in a Monad."""
    ...

  """An unwrappable has the ability to export the internal wrapped value."""
  def unwrap(self) -> WrappableValue:
    ...

BindableValue = TypeVar('BindableValue')
class Bindable(Wrappable, Protocol[BindableValue]):
  def bind(self, next_func: Callable[[BindableValue], Bindable[BindableValue]]) -> 'Bindable[BindableValue]':
    """
    Enables chaining functions in the effect world.
    """
    ...

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

MonadValue = TypeVar('MonadValue', covariant=True)
class Monad(Bindable, Protocol[MonadValue]):
  ...
    

ApplicativeValue = TypeVar('ApplicativeValue', covariant=True)
WrappedValue = TypeVar('WrappedValue', covariant=False)
ApplyResult = TypeVar('ApplyResult', covariant=False)
class Applicative(Wrappable, Protocol[ApplicativeValue]):
  """
  An applicative functor has the following characteristics:

  It is an effect type.
  It has a pure function.
  It has a function that combines two effects into one. This is typically called ap, apply, or pair.
  It must adhere to the Applicative Functor Laws.
  """
  def apply(
    self: Applicative[Callable[[WrappedValue], ApplyResult]], 
    other: Wrappable[WrappedValue]
    ) -> 'Applicative[ApplyResult]':
    ...

JustValue = TypeVar('JustValue')
class Just(Monad, Hashable, Generic[JustValue]):
  def __init__(self, value: JustValue) -> None:
    super().__init__()
    self._value = value 

  def unwrap(self) -> JustValue:
    return self._value
  
  def wrap(self, value: JustValue) -> 'Just[JustValue]':
    return Just(value)
  
  def bind(self, next_func: Callable[[JustValue], Bindable[JustValue]]) -> 'Bindable[JustValue]':
    return next_func(self.unwrap())
  
  def __eq__(self, other: object) -> bool:
    if hasattr(other, 'unwrap'):
      return self._value.__eq__(cast(Wrappable,other).unwrap())
    else:
      return self._value.__eq__(other)
    
  def __hash__(self) -> int:
    # Use the unwrapped value converted to a tuple has the 
    # hash value.
    return hash((self._value))
  
"""
Either is as an alternative to Optional for dealing with possibly 
missing values or errors. In this usage, None is replaced with a
Left which can contain useful information. Right takes the place
Some. 

Convention dictates that Left is used for failure and Right is 
used for success.
"""

class EitherType(Enum):
  Left = auto()
  Right = auto()

L = TypeVar('L')
S = TypeVar('S')
R = TypeVar('R')

class EitherException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class Either(Applicative, Monad, Generic[L, R]):
  def __init__(self, value: Any, side: EitherType) -> None:
    self._value = value
    self._side = side

  @staticmethod
  def right(value: R) -> Either[Any, R]:
    return Either(value, EitherType.Right)

  @staticmethod
  def left(value:L) -> Either[L, Any]:
    return Either(value, EitherType.Left)

  def is_left(self) -> bool:
    return self._side == EitherType.Left
  
  def is_right(self) -> bool:
    return self._side == EitherType.Right
  
  def wrap(self, value: Any) -> 'Either':
    if self.is_right():
      return Either.right(value)
    else: 
      return Either.left(value)
    
  def unwrap(self) ->  Any:
    return self._value
  
  def apply(
    self: 'Either[L, Callable[[S], R]]', 
    other: Wrappable[S]
  ) -> 'Either':
    """Applies a contained function on another Either's right value."""
    if self.is_left():
      return self
    elif isinstance(other, Either) and other.is_left():
      return other 
    else:
      if not callable(self._value):
        raise EitherException('Tried to call apply on an instance of Either that was not a Callable.')
      return Either.right(self._value(other.unwrap()))
  
  def bind(self, func: Callable[[BindableValue], Bindable[BindableValue]]) -> 'Bindable[BindableValue]':
    """Binds a function to the Right side.
    Returns an Either.
    """
    if self.is_left():
      return self  
    else:
      result: Bindable[Any] = func(self.unwrap())
      if not isinstance(result, Either):
        return Either.right(result)
      return result

MaybeValue = TypeVar('MaybeValue')
class Maybe(Wrappable, Functor, Protocol[MaybeValue]):
  @staticmethod
  def from_optional(value: MaybeValue | None) -> 'Maybe[MaybeValue]':
    if value is None:
      return Nothing()
    else:
      return Something(value)
    
  def is_something(self) -> bool:
    """
    Returns if the instance is a Something.
    """
    ...

class Nothing(Maybe[Any]):
  def __init__(self, value: None = None) -> None:
    super().__init__()
    self._value = value

  def wrap(self, value: Any) -> Nothing:
    return self
  
  def unwrap(self) -> Any:
    return None
  
  def map(self, func: Callable[[Any], B]) -> Maybe[B]:
    """Map doesn't do anything on Nothing."""
    return self
  
  def is_something(self) -> bool:
    """
    Returns if the instance is a Something.
    """
    return False 

class Something(Maybe[MaybeValue]):
  def __init__(self, value: MaybeValue) -> None:
    super().__init__()
    self._value = value

  def wrap(self, value: Any) -> Something:
    return Something(value)
  
  def unwrap(self) -> MaybeValue:
    return self._value

  def map(self, func: Callable[[MaybeValue], B]) -> Maybe[B]:
    return Something(func(self.unwrap()))
  
  def is_something(self) -> bool:
    """
    Returns if the instance is a Something.
    """
    return True