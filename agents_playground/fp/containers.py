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
from collections.abc import MutableSet
from typing import Callable, Dict, Generic, Iterable, List, Set, TypeVar


from agents_playground.fp import Applicative, Functor, Wrappable
from agents_playground.fp.functions import chain, compose

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

class FPDict(UserDict[FPDictKey, FPDictKeyValue], Functor, Wrappable):
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
  
FPSetItem = TypeVar('FPSetItem')
FPNewSetItem = TypeVar('FPNewSetItem')
class FPSet(MutableSet[FPSetItem], Functor, Applicative):
  def __init__(self, items: Iterable | None = None):
    self._data: List[FPSetItem] = []
    if items is None:
      return
    for item in items:
      if item not in self._data:
        self.add(item)

  def __contains__(self, item):
    return item in self._data

  def __iter__(self):
      return iter(self._data)

  def __len__(self):
      return len(self._data)
  

  def __repr__(self) -> str:
    return f"FPSet({self._data})"

  def add(self, item):
    if item not in self._data:
      self._data.append(item)

  def discard(self, item):
    try:
      del self._data[self._data.index(item)]
    except ValueError:
      pass

  def map(
    self, 
    func: Callable[[FPSetItem], FPNewSetItem]
  ) -> FPSet[FPNewSetItem]:
    """
    Applies a function to all of the values in the dict and 
    returns a new FPDict.
    """
    # return FPDict(list(map(func, self.data)))
    return FPSet([func(item) for item in self._data ])
  
  def wrap(
    self, 
    a_set: Set[FPSetItem]
  ) -> FPSet[FPSetItem]:
    return FPSet(a_set)
  
  def unwrap(self) -> Set[FPSetItem]:
    return set(self._data)
  
  def apply(
    self: FPSet[Callable[[B], B]], 
    other: Wrappable[B]) -> 'FPSet[B]':
    """
    If this instance of FPSet contains functions, then apply them 
    to the provided Wrappable.
    """
    if isinstance(other, Iterable):
      results = [chain(*self._data)(wrapper.unwrap()) for wrapper in other]
    else:
      results = [chain(*self._data)(other.unwrap())]
      
    return FPSet(results)