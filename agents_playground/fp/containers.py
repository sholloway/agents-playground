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
from collections.abc import Collection, MutableSet
from typing import Callable, Dict, Generic, Iterable, List, Set, TypeVar, cast


from agents_playground.fp import Applicative, Either, Functor, Nothing, Something, Wrappable
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
    return self.data.copy()
  
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
    return self.data.copy()
  
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
  
class FPStackIndexError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)
  
StackItem = TypeVar('StackItem')
NewStackItem = TypeVar('NewStackItem')
class FPStack(Collection [Wrappable[StackItem]], Wrappable):
  """A functional stack that works with wrappable items."""
  def __init__(self, items: Iterable[Wrappable[StackItem]] | None = None) -> None:
    self._data: List[Wrappable[StackItem]] = []
    if items is not None:
      self._data.extend(items)

  def push(self, item: Wrappable[StackItem]) -> None:
    """Given an item append it to the stack."""
    self._data.append(item)

  def pop(self) -> Wrappable:
    if len(self._data) > 0:
      return self._data.pop()
    else:
      raise FPStackIndexError('Pop from empty list.')

  def __contains__(self, item):
    """Enables using 'in' with the FPStack."""
    return item in self._data

  def __iter__(self):
    """Enables iterating over the stack without popping it."""
    return iter(self._data)

  def __len__(self):
    """Enables using len() with the FPStack."""
    return len(self._data)
  
  def wrap(self, items: Iterable[Wrappable]) -> Wrappable:
    return FPStack(items)
  
  def unwrap(self) -> List[Wrappable[StackItem]]:
    return self._data.copy()
  
  def __eq__(self, other: object) -> bool:
    if hasattr(other, 'unwrap'):
      return self._data.__eq__(cast(Wrappable,other).unwrap())
    else:
      return self._data.__eq__(other)


class FPQueue:
  pass 