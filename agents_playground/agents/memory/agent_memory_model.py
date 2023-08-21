from collections.abc import MutableMapping
from typing import Iterable, Iterator
from agents_playground.agents.memory.collections import SupportsKeysAndGetItem, SupportsMemoryMethods

from agents_playground.agents.memory.memory_container import MemoryContainer
from agents_playground.fp.containers import FPDict

class AgentMemoryModelError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class AgentMemoryModel(MutableMapping[str, MemoryContainer], SupportsMemoryMethods): 
  """
  Represents an agent's mind. What they're able to learn and remember. 
  Adheres to the AgentMemoryLike protocol contract.
  """
  def __init__(self, dict = None, **kwargs) -> None:
    super().__init__()
    self._data: FPDict[str, MemoryContainer] = FPDict()
    if dict is not None:
      self._data.update(dict)
    if kwargs:
      self._data.update(kwargs)

  def __getitem__(self, key: str) -> MemoryContainer:
    """
    Provide the ability to fetch an item by its key.
    Raises a KeyError if nothing is found. 

    Examples:
      >>> memory_model['sense_memory']
    """
    return self._data[key]
    
  def __setitem__(self, key: str, value: MemoryContainer) -> None:
    """Enables setting a container.
    
    Args:
      key (str): The unique identifier for the container.
      container (MemoryContainer): The storage mechanism for a group of memories.

    Examples:
      >>> memory_model['long_term_memory'] = FPSet[Memory]().
    
    """
    self._data[key] = value

  def __delitem__(self, key: str) -> None:
    """
    Provides the ability to remove a container from the memory model.

    Examples:
      >>> del memory_model['long_term_memory']
    """
    if key in self._data:
      del self._data[key]

  def __iter__(self) -> Iterator[str]:
    """Provides an iterator for the memory container keys."""
    return iter(self._data)
  
  def __len__(self) -> int:
    return len(self._data)
  
  def __contains__(self, key: object) -> bool: 
    return key in self._data

  def __eq__(self, other: object) -> bool:
    return self._data.__eq__(other)
  
  def __ne__(self, other: object) -> bool: 
    return self._data.__ne__(other)

  def get(self, key: str, default: MemoryContainer | None = None) -> MemoryContainer | None: 
    return self._data.get(key, default)
  
  def pop(self, key: str) -> MemoryContainer:
    return self._data.pop(key)
  
  def setdefault(self, key: str, default: MemoryContainer) -> MemoryContainer:
    if key in self._data:
      return self._data[key]
    else:
      self._data[key] = default
      return default 
  
  def update(
    self, 
    m: SupportsKeysAndGetItem[str, MemoryContainer] | Iterable[tuple[str, MemoryContainer]], 
    **kwargs: MemoryContainer
  ) -> None:
    self._data.update(m, **kwargs)

  def add(self, key: str, container: MemoryContainer) -> None:
    """Adds a memory container with a key for retrieval.

    Args:
      key (str): The unique identifier for the container.
      container (MemoryContainer): The storage mechanism for a group of memories.
    
    Examples:
      >>> memory_model.add('sense_memory', FPList[Memory]())
      >>> memory_model.add(key = 'working_memory', container = TTLStore[str, Memory]())
      >>> memory_model['long_term_memory'] = FPSet[Memory]().
    """
    if key in self._data:
      raise AgentMemoryModelError(f'A memory container with the key {key} is already registered in the AgentMemoryModel.')
    self._data[key] = container

  def tick(self) -> None:
    """
    Notifies each memory container that the simulation has 
    advanced one frame.
    """
    container: MemoryContainer
    for container in self._data.values():
      if(hasattr(container, 'tick')):
        container.tick()
