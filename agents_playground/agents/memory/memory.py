from __future__ import annotations

from typing import Callable, Generic, Hashable, TypeVar, cast

from agents_playground.fp import Bindable, Maybe, Monad, Nothing, Something, Wrappable

MemoryValue = TypeVar('MemoryValue')
MemoryMetadata = TypeVar('MemoryMetadata')

class Memory(Monad, Hashable, Generic[MemoryValue, MemoryMetadata]):
  """
  Represents something an agent can retain in their brain. 
  This could be a sense, a fact, a skill, really anything. 
  """
  def __init__(
    self, 
    core_memory: MemoryValue, 
    memory_metadata: MemoryMetadata | None = None
  ) -> None:
    """
    Create a new instance of a Memory.

    Args:
      core_memory (MemoryValue): The main concept that this memory wraps.
      memory_metadata (Maybe[MemoryMetadata]): An optional piece of metadata that a memory can contain.
    """
    self._core_memory = core_memory
    self._memory_metadata = memory_metadata 

  def wrap(
    self, 
    core_memory: MemoryValue
  ) -> 'Memory[MemoryValue, Nothing]':
    return Memory(
      core_memory = core_memory, 
      memory_metadata = Nothing()
    )
  
  @staticmethod
  def instance(core_memory: MemoryValue) -> Memory:
    return Memory(
      core_memory = core_memory, 
      memory_metadata = Nothing()
    )

  def unwrap(self) -> MemoryValue:
    return self._core_memory
  
  def metadata(self) -> Maybe[MemoryMetadata]:
    return Nothing() if self._memory_metadata is None else Something(self._memory_metadata)
  
  def bind(
    self, 
    next_func: Callable[[MemoryValue], Bindable[MemoryValue]]
  ) -> 'Bindable[MemoryValue]':
    return next_func(self.unwrap())
  
  # Note: It may be better to compare objects using a tuple of
  # all the attributes. Should TTL and memory_metadata be included
  # in the equality check?
  def __eq__(self, other: object) -> bool:
    if hasattr(other, 'unwrap'):
      return self._core_memory.__eq__(cast(Wrappable, other).unwrap())
    else:
      return self._core_memory.__eq__(other)
    
  def __hash__(self) -> int:
    return hash((self._core_memory, self._memory_metadata))
  
  def __repr__(self) -> str:
    return f'Wrapped: {self._core_memory}, Meta: {self._memory_metadata}'
    