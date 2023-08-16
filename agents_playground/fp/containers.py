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
from decimal import Decimal
from typing import Any, Callable, Dict, Generic, Iterable, List, Protocol, Set, TypeVar, cast
from agents_playground.counter.counter import Counter


from agents_playground.fp import Applicative, Either, Functor, Nothing, Something, Wrappable
from agents_playground.fp.functions import chain, compose

class FPCollectionError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

FPCollectionItem = TypeVar('FPCollectionItem', covariant=False)
FPCollectionItemMetadata = TypeVar('FPCollectionItemMetadata', contravariant=True)
class FPCollection(
  Collection[FPCollectionItem], 
  Functor[FPCollectionItem], 
  Applicative[FPCollectionItem], 
  Protocol[FPCollectionItem, FPCollectionItemMetadata]):
  
  def contain(self, item: FPCollectionItem, metadata: FPCollectionItemMetadata | None = None) -> None:
    """A generalized add method.

    Args:
      item (FPCollectionItem): The item to add to the collection.
      metadata (FPCollectionItemMetadata): Optional metadata about the item. This could vary depending on the implementing class.
    """
    ...

A = TypeVar('A')
B = TypeVar('B')
class FPList(UserList[A], FPCollection[A, Any]):
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
  
  def contain(self, item: A, _: Any | None = None) -> None:
    self.data.append(item)
  
FPDictKey = TypeVar('FPDictKey')
FPDictValue = TypeVar('FPDictValue')
FPDictKeyNewValue = TypeVar('FPDictKeyNewValue')

class FPDict(UserDict[FPDictKey, FPDictValue], FPCollection[FPDictValue, FPDictKey]):
  def __init_subclass__(cls) -> None:
    return super().__init_subclass__()

  def map(
    self, 
    func: Callable[[FPDictValue], FPDictKeyNewValue]
  ) -> FPDict[FPDictKey, FPDictKeyNewValue]:
    """
    Applies a function to all of the values in the dict and 
    returns a new FPDict.
    """
    # return FPDict(list(map(func, self.data)))
    return FPDict({ i: func(j) for i,j in self.data.items() })
  
  def wrap(
    self, 
    a_dict: Dict[FPDictKey, FPDictValue]
  ) -> FPDict[FPDictKey, FPDictValue]:
    return FPDict(a_dict)
  
  def unwrap(self) -> Dict[FPDictKey, FPDictValue]:
    return self.data.copy()
  
  def apply(
    self: FPDict[FPDictKey, Callable[[B], B]], 
    other: Wrappable[B]) -> FPList[B]:
    """
    If this instance of FPDict contains functions, then apply them 
    to the provided Wrappable.
    """
    if isinstance(other, Iterable):
      results = [chain(*self.data.values())(wrapper.unwrap()) for wrapper in other]
    else:
      results = [chain(*self.data.values())(other.unwrap())]
      
    return FPList(results)
  
  def contain(self, item: FPDictValue, metadata: FPDictKey | None = None) -> None:
    if metadata is not None:
      self.data[metadata] = item
    else:
      raise FPCollectionError('Metadata value required for add(item, metadata) on FPDict.')
  
FPSetItem = TypeVar('FPSetItem')
FPNewSetItem = TypeVar('FPNewSetItem')
class FPSet(MutableSet[FPSetItem], FPCollection[FPSetItem, Any]):
  def __init__(self, items: Iterable | None = None):
    self._data: List[FPSetItem] = []
    if items is None:
      return
    for item in items:
      if item not in self._data:
        self.contain(item)
  
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
class FPStack(FPCollection[Wrappable[StackItem], Any]):
  """A functional stack that works with wrappable items."""
  def __init__(self, items: Iterable[Wrappable] | None = None) -> None:
    self._data: List[Wrappable] = []
    if items is not None:
      self._data.extend(items)

  def push(self, item: Wrappable) -> None:
    """Given an item append it to the stack."""
    self._data.append(item)

  def contain(self, item: Wrappable[StackItem], _: Any | None = None) -> None:
    return self.push(item)

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
  
  def unwrap(self) -> List[Wrappable]:
    return self._data.copy()
  
  def __eq__(self, other: object) -> bool:
    if hasattr(other, 'unwrap'):
      return self._data.__eq__(cast(Wrappable,other).unwrap())
    else:
      return self._data.__eq__(other)
    
  def map(self, func: Callable[[Wrappable], B]) -> Functor[B]:
    raise Exception('Map is not supported on FPStack.')
  
  def apply(
    self: Applicative, 
    other: Wrappable
  ) -> Applicative:
    raise Exception('Apply is not supported on FPStack.')
  

FPStoreItem = TypeVar('FPStoreItem')
FPStoreTTL = TypeVar('FPStoreTTL', int, float, Decimal)
class FPTTLStore(FPCollection[FPStoreItem, FPStoreTTL]):
  """
  A container that automatically removes items with their time to live expires.
  Items must be hashable.
  """
  def __init__(self, initial_dict: Dict[FPStoreItem, Counter] | None = None) -> None:
    if initial_dict is None:
      self._data: Dict[FPStoreItem, Counter] = {}
    else:
      self._data = initial_dict

  def wrap(self, value: FPStoreItem) -> Wrappable:
    raise NotImplementedError('FPTTLStore.wrap() is not implemented.')
  
  def unwrap(self) -> Any:
    return self._data.copy()
  
  def map(self, func: Callable[[FPStoreItem], B]) -> Functor[B]:
    """
    Applies a function to all the items in the store and returns 
    a new FPTTLStore. The original items TTL are preserved.
    """
    return FPTTLStore({ func(i): j for i,j in self._data.items() })
  
  def apply(
    self: FPTTLStore[Callable[[B], B], FPStoreTTL], 
    other: Wrappable[B]) -> FPList[B]:
    """
    If this instance of FPTTLStore contains functions, then apply them 
    to the provided Wrappable.
    """
    if isinstance(other, Iterable):
      results = [chain(*self._data.keys())(wrapper.unwrap()) for wrapper in other]
    else:
      results = [chain(*self._data.keys())(other.unwrap())]
      
    return FPList(results)
  

  """
  This is a mess. Trying to have a consistent contract across 
  multiple storage types is proving to be ugly and ineffective.

  Todo:
  - Look at Python patterns for overloading and overridding. 
  """
  def contain(self, item: FPStoreItem, ttl: FPStoreTTL | None = None) -> None:
    if ttl is not None:
      self._data[item] = item
    else:
      raise FPCollectionError('Metadata value required for add(item, metadata) on FPDict.')