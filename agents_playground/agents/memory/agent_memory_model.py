from agents_playground.agents.memory.collections import SupportsMemoryMethods
from agents_playground.agents.memory.memory_container import MemoryContainer
from agents_playground.fp.containers import FPDict

class AgentMemoryModelError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class AgentMemoryModel(FPDict[str, MemoryContainer], SupportsMemoryMethods): 
  """
  Represents an agent's mind. What they're able to learn and remember. 
  Adheres to the AgentMemoryLike protocol contract.
  """
  def __init__(self, dict = None, **kwargs) -> None:
    super().__init__()
    if dict is not None:
      self.data.update(dict)
    if kwargs:
      self.data.update(kwargs)

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
    if key in self.data:
      raise AgentMemoryModelError(f'A memory container with the key {key} is already registered in the AgentMemoryModel.')
    self.data[key] = container

  def tick(self) -> None:
    """
    Notifies each memory container that the simulation has 
    advanced one frame.
    """
    container: MemoryContainer
    for container in self.data.values():
      container.tick()
