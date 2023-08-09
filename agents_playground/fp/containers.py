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
from typing import Callable, Dict, Generic, List, TypeVar

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
  
FPDictKey = TypeVar('FPDictKey')
FPDictKeyValue = TypeVar('FPDictKeyValue')
FPDictKeyNewValue = TypeVar('FPDictKeyNewValue')

class FPDict(UserDict[FPDictKey, FPDictKeyValue], Functor, Applicative):
  def __init_subclass__(cls) -> None:
    return super().__init_subclass__()

  def map(
    self, 
    func: Callable[[FPDictKeyValue], FPDictKeyNewValue]
  ) -> FPDict[FPDictKey, FPDictKeyNewValue]:
    """
    Applies a function to all of the values in the dict and 
    returns a new FPDict.
    """
    # return FPDict(list(map(func, self.data)))
    return FPDict({ i: func(j) for i,j in self.data.items() })
  
  def wrap(
    self, 
    a_dict: Dict[FPDictKey, FPDictKeyValue]
  ) -> FPDict[FPDictKey, FPDictKeyValue]:
    return FPDict(a_dict)
  
  def unwrap(self) -> Dict[FPDictKey, FPDictKeyValue]:
    return self.data
  
  def apply(
    self: FPDict[FPDictKey, Callable[[B], B]], 
    other: Wrappable[B]
  ) -> FPDict[FPDictKey, B]:
    """
    If this instance of FPDict contains functions as values, 
    then apply them to the provided Wrappable.
    """
    raise Exception('Not Implemented Yet')