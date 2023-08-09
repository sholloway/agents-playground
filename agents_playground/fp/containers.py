"""
A collection of containers that enable using the Pythonic contracts
but also enable FP capabilities.


TODO
- List
- Dictionary
- Set
- Stack
- Queue
- TTLStore
"""

from __future__ import annotations

from collections import UserDict, UserList
from typing import Callable, Generic, List, TypeVar

from pyparsing import Iterable

from agents_playground.fp import Applicative, Functor, Wrappable
from agents_playground.fp.functions import chain

A = TypeVar('A')
B = TypeVar('B')


class FPList(UserList[A], Functor[A], Applicative[A]):
  def __init_subclass__(cls) -> None:
    return super().__init_subclass__()
  
  def map(self, func: Callable[[A], B]) -> FPList[B]:
    """
    Applies a function to all of the elements in the list and 
    returns a new FPList.
    """
    return FPList(list(map(func, self.data)))
  
  def wrap(self, values: List[A]) -> FPList[A]:
    return FPList[A](values)
  
  def unwrap(self) -> List[A]:
    return self.data
  
  def apply(
    self: FPList[Callable[[B], B]], 
    other: Wrappable[B]) -> 'FPList[B]':
    """
    If this instance of FPList contains functions, then apply them 
    to the provided Wrappable.
    """
    if isinstance(other, Iterable):
      results = [chain(*self.unwrap())(wrapper.unwrap()) for wrapper in other]
    else:
      results = [chain(*self.unwrap())(other.unwrap())]
      
    return FPList(results)
  
class FPDict(UserDict):
  def __init_subclass__(cls) -> None:
    return super().__init_subclass__()

  