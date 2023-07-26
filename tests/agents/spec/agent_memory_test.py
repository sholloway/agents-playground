from __future__ import annotations
from abc import abstractmethod
from math import inf as INFINITY
from typing import Any, Dict, Generic, List, Protocol, Set, TypeVar, cast

from agents_playground.agents.spec.tick import Tick as FrameTick
from agents_playground.containers.ttl_store import TTLStore

class FakeAgent:
  """Simplified stand in for AgentLike."""
  def __init__(self, memory: AgentMemoryLike) -> None:
    self.memory = memory

"""
What can be done to a memory?
Remember, forget, 
"""
T = TypeVar('T')
class Memory(Generic[T]):
  def __init__(self, item: T) -> None:
    super().__init__()

  

Tick = int # Represents one frame in the simulation.

class MemoryBankLike(FrameTick, Protocol):
  """Represents a portion a an agent's memory.
  A memory bank could have a variety of storage mechanisms.
  A stack, a dict, a tree. However, fundamentally, all memory 
  banks have the ability to remember, recall, and forget.
  """
  name: str
  
  def remember(self, label: str, item: Any, ttl: Tick = cast(int,INFINITY)) -> None:
    """Store something in the memory bank's store."""
    return 

  def recall(self, label: str) -> Any:
    """Summon a memory by its label"""
    return 
  
  def forget(self, label: str) -> None:
    """Remove a memory from the memory bank's store."""
    return
  
  def forget_all(self, label: str) -> None:
    """Remove all memories from the memory bank's store."""
    return
  
  def memories(self) -> List[Memory]:
    """Return all current memories in the memory bank."""
    return []

class NoMemoryBank(MemoryBankLike):
  def __init__(self) -> None:
    super().__init__()
    self.name = self.__class__.__name__

  def tick(self) -> None:
    return

class AgentMemoryError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

MemoryBankName = str
_missing_memory_bank = NoMemoryBank()

class AgentMemoryLike(FrameTick, Protocol):
  memory_banks: Dict[MemoryBankName, MemoryBankLike]

  def tick(self) -> None:
    for memory_bank in self.memory_banks.values():
      memory_bank.tick()

  def register(self, memory_bank: MemoryBankLike) -> None:
    if memory_bank.name not in self.memory_banks:
      self.memory_banks[memory_bank.name] = memory_bank
    else: 
      raise AgentMemoryError(f'The memory bank {memory_bank.name} is already registered.')

  def memory_bank(self, name: str) -> MemoryBankLike:
    return self.memory_bank.get(name, _missing_memory_bank)

class DefaultAgentMemory(AgentMemoryLike):
  def __init__(self, initial_memory_banks: List[MemoryBankLike] = []) -> None:
    super().__init__()
    self.memory_banks: Dict[MemoryBankName, MemoryBankLike] = {}
    for memory_bank in initial_memory_banks:
      self.register(memory_bank)

class NoMemory:
  """
  A memory definition for a dumb agent that cannot remember anything.
  Does not extend AgentMemoryLike but implements the contract.
  """
  def __init__(self) -> None:
    self.memory_banks: Dict[MemoryBankName, MemoryBankLike] = {}

  def tick(self) -> None:
    return 
  
  def register(self, memory_bank: MemoryBankLike) -> None:
    return
  
  def memory_bank(self, name: str) -> MemoryBankLike:
    return self.memory_bank.get(name, _missing_memory_bank)
  
class StackMemoryBank:
  """Naive implementation of a stack based memory bank."""

  def __init__(self) -> None:
    self._stack: List[Memory] = []
    self.name = self.__class__.__name__

  def tick(self) -> None:
    return
  
  def remember(self, label: str, item: Memory, ttl: Tick = cast(int,INFINITY)) -> None:
    """Store something in the memory bank's store."""
    self._stack.append(item)

  def recall(self, label: str) -> Memory:
    """Summon a memory by its label"""
    return self._stack.pop()
  
  def forget(self, label: str) -> None:
    """Remove a memory from the memory bank's store.
    This doesn't make sense for a stack based memory bank.
    """
    return
  
  def forget_all(self, label: str) -> None:
    """Remove all memories from the memory bank's store."""
    self._stack.clear()
  
  def memories(self) -> List[Memory]:
    """Return all current memories in the memory bank."""
    return self._stack
  
class SetMemoryBank:
  """
  A naive implementation of a memory bank that uses a set for 
  internal storage.
  """
  def __init__(self) -> None:
    self._memory_set: Set[Memory] = set()
    self.name = self.__class__.__name__

  def remember(self, label: str, item: Memory, ttl: Tick = cast(int,INFINITY)) -> None:
    """Store something in the memory bank's store."""
    self._memory_set.add(item)

class FakeSensoryMemoryBank:
  def __init__(self) -> None:
    self.name = self.__class__.__name__
    self.memory_store = TTLStore()

  def tick(self) -> None:
    return

  def remember(self, label: str, item: Any, ttl: Tick = cast(int,INFINITY)) -> None:
    """Store something in the memory bank's store."""
    self.memory_store.store(item, ttl)

  def recall(self, label: str) -> Any:
    """Summon a memory by its label"""
    self.memory_store.
  
  def forget(self, label: str) -> None:
    """Remove a memory from the memory bank's store."""
    return
  
  def forget_all(self, label: str) -> None:
    """Remove all memories from the memory bank's store."""
    return
  
  def memories(self) -> List[Memory]:
    """Return all current memories in the memory bank."""
    return []

class FakeWorkingMemoryBank:
  pass

class FakeLongTermMemory: 
  pass

class TestAgentMemory:
  def test_extensibility(self) -> None:
    dumb_agent = FakeAgent(memory = NoMemory())
    default_agent = FakeAgent(memory = DefaultAgentMemory())
    push_down_automata = FakeAgent(
      memory = DefaultAgentMemory(
        initial_memory_banks=[StackMemoryBank()]
      )
    )
    three_tier_agent = DefaultAgentMemory(
      initial_memory_banks=[
        FakeSensoryMemoryBank(),
        # FakeWorkingMemoryBank(),
        # FakeLongTermMemory()
      ]
    )

  
"""
Current List of Challenges
- What is a memory? Perhaps we need a memory container class. 
  This is to enable things like sensations, recognitions, skills, 
  facts. 
  Monad example: https://github.com/jasondelaat/pymonad/blob/release/pymonad/monad.py

  Look at the school of common monads for inspiration.
  Consider generics.

- The contract for MemoryBankLike doesn't work depending on the 
  internal storage mechanism. Parameters like ttl and label don't 
  make sense for most storage types. 
  This is where I wonder if monads and functors could simplify things.

- How should memory retrieval work? Need to have a generic 
  enough contract to support internal lists, dicts, trees, etc.

- How to deal with multi-storage memory bank like long term memory (memories, skills, knowledge)?
Options
  - Flatten it. Rather than have the hierarchy be Sensory Memory, Working Memory, Long Term Memory
    have it be: Sensory Memory, Working Memory, long term memories, skills, knowledge.
    (I like this approach better.)
  - Use the composite pattern.
"""