"""
A collection of containers that enable using the Pythonic contracts
but also enable FP capabilities.


Containers
Sequence Focused
- List
- Stack
- Queue

Node Focused
- Tree
- Heap

Hash Focused
- Set
- Dictionary
- TTLStore
"""

from __future__ import annotations

from collections import UserDict, UserList
from collections.abc import Collection, MutableSet
from typing import Any, Callable, Dict, Iterable, List, Set, TypeVar, cast

from agents_playground.agents.spec.tick import Tick
from agents_playground.fp import Applicative, Functor, Wrappable
from agents_playground.fp.functions import chain

A = TypeVar('A')
B = TypeVar('B')
class FPList(UserList[A], Applicative, Functor, Tick):
  def __init_subclass__(cls) -> None:
    return super().__init_subclass__()
  
  def __init__(
    self, 
    initial_list: List | UserList | None = None,
    tick_action: Callable[[FPList[A]], None] | None = None
  ) -> None:
    super().__init__(initial_list)
    self._tick_action = tick_action

  def tick(self) -> None:
    if self._tick_action:
      self._tick_action(self)
  
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
  
  def contain(self, item: A, _: Any | None = None) -> None:
    self.data.append(item)
  
FPDictKey = TypeVar('FPDictKey')
FPDictValue = TypeVar('FPDictValue')
FPDictKeyNewValue = TypeVar('FPDictKeyNewValue')

class FPDict(UserDict[FPDictKey, FPDictValue], Functor, Tick, Wrappable):
  """
  A functional orientated dictionary that support Tick. 

  To specify a tick function use the tick_action property.

  Examples:
    >>> fpd = FPDict({'a':123, 'b':456})
    >>> fpd = FPDict('a'=123, 'b'=456)
    >>> fpd = FPDict({'c':789}, a=123, b=456)
  """
  def __init_subclass__(cls) -> None:
    return super().__init_subclass__()

  def __init__(self, dict=None, **kwargs):
    super().__init__(dict, **kwargs)
    self.tick_action: Callable[[FPDict[FPDictKey, FPDictValue]], None] | None = None

  def tick(self) -> None:
    if self.tick_action:
      self.tick_action(self)

  def map(
    self, 
    func: Callable[[FPDictValue], FPDictKeyNewValue]
  ) -> FPList[FPDictKeyNewValue]:
    """
    Applies a function to all of the values in the dict and 
    returns a new FPDict.
    """
    return FPList([ func(value) for value in self.data.values() ])
  
  def wrap(
    self, 
    a_dict: Dict[FPDictKey, FPDictValue]
  ) -> FPDict[FPDictKey, FPDictValue]:
    return FPDict(a_dict)
  
  def unwrap(self) -> Dict[FPDictKey, FPDictValue]:
    return self.data.copy()
  
  
FPSetItem = TypeVar('FPSetItem')
FPNewSetItem = TypeVar('FPNewSetItem')
class FPSet(MutableSet[FPSetItem], Applicative, Functor, Tick):
  def __init__(self, 
    items: Iterable | None = None, 
    tick_action: Callable[[FPSet[FPSetItem]], None] | None = None
  ) -> None:
    self._data: List[FPSetItem] = []
    self._tick_action = tick_action
    if items is None:
      return
    for item in items:
      if item not in self._data:
        self.contain(item)
  
  def tick(self) -> None:
    if self._tick_action:
      self._tick_action(self)

  def __contains__(self, item):
    return item in self._data

  def __iter__(self):
      return iter(self._data)

  def __len__(self):
      return len(self._data)
  
  def __repr__(self) -> str:
    return f"FPSet({self._data})"
   
  def contain(self, item: FPSetItem, _: Any | None = None):
    if item not in self._data:
      self._data.append(item)

  def add(self, value: FPSetItem) -> None:
    self.contain(value)

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
    returns a new FPSet.
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
OtherStackItem = TypeVar('OtherStackItem')
class FPStack(Collection[StackItem], Tick, Wrappable):
  """A functional stack."""
  def __init__(self, 
    items: Iterable[StackItem] | None = None,
    tick_action: Callable[[FPStack[StackItem]], None] | None = None  
  ) -> None:
    self._data: FPList[StackItem] = FPList()
    self._tick_action = tick_action
    if items is not None:
      self._data.extend(items)

  def tick(self) -> None:
    if self._tick_action:
      self._tick_action(self)

  def push(self, item: StackItem) -> None:
    """Given an item append it to the stack."""
    self._data.append(item)

  def pop(self) -> StackItem:
    """Return the item on the top of the stack."""
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
  
  def wrap(self, items: Iterable[OtherStackItem]) -> FPStack[OtherStackItem]:
    return FPStack[OtherStackItem](items)
  
  def unwrap(self) -> FPList[StackItem]:
    return self._data.copy()
  
  def __eq__(self, other: object) -> bool:
    if hasattr(other, 'unwrap'):
      return self._data.__eq__(cast(Wrappable,other).unwrap())
    else:
      return self._data.__eq__(other)