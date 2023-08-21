from __future__ import annotations
from typing import Callable, Iterator, TypeVar

import agents_playground.agents.memory.collections as memory_stores
from agents_playground.fp import Bindable, Monad

MemoryContainerStorage = TypeVar("MemoryContainerStorage", 
  memory_stores.Collection, 
  memory_stores.Sequence, 
  memory_stores.MutableSequence, 
  memory_stores.Set,
  memory_stores.MutableSet,
  memory_stores.Mapping,
  memory_stores.MutableMapping,
  memory_stores.SupportsTTL
)

class MemoryContainer(
  memory_stores.Collection[MemoryContainerStorage], 
  Monad[MemoryContainerStorage]
):
  """
  This is a memory bank. It is a storage container for memories.
  It provides a wrapper for housing the various possible storage types.
  """
  def __init__(self, storage: MemoryContainerStorage) -> None:
    self._storage = storage

  def tick(self) -> None:
    """Signal to the items in the memory storage that a frame has passed."""
    self._storage.tick()

  def wrap(self, storage_system: MemoryContainerStorage) -> MemoryContainer:
    return MemoryContainer(storage_system)
  
  def unwrap(self) -> MemoryContainerStorage:
    return self._storage
  
  def bind(self, next_func: Callable[[MemoryContainerStorage], Bindable]) -> Bindable:
    return next_func(self._storage)
  
  def __contains__(self, item: object) -> bool:
    return item in self._storage
  
  def __iter__(self) -> Iterator[MemoryContainerStorage]:
    return iter(self._storage)
  
  def __len__(self) -> int:
    return len(self._storage)