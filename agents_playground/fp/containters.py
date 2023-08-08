"""
A collection of containers that enable using the Pythonic contracts
but also enable FP capabilities.
"""

from __future__ import annotations

from collections import UserList
from typing import Callable, Generic, List, TypeVar

from agents_playground.fp import Applicative, Functor, Wrappable

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
    self, 
    other: Wrappable[A]) -> 'Applicative[A]':
    """
    If this instance of FP contains functions, then apply them 
    to the provided Wrappable.
    """
    raise Exception('Not Implemented Yet')