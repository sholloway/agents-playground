from __future__ import annotations

from abc import abstractmethod
from math import inf as INFINITY
from typing import Any, Callable, Dict, Generic, List, Protocol, Set, TypeVar, cast

from agents_playground.agents.spec.tick import Tick as FrameTick
from agents_playground.containers.ttl_store import TTLStore

"""
Can FP help with the Memory model?
For a memory, I need a generic container that can bind things like
- expire_on_ttl
- enable_skill_on_ttl

I think the trick here is to have memory "containers" that systems
can apply functions to. 

So, rather than memory.learn() or memory.forget() it's 
Memory.wrap(learn).apply(Memory) and Memory.wrap(some_fact).bind(expire_on_ttl)

For example, a skill is a memory with a Time To Learn (ttl)
skill = Memory(value=CutWood, ttl=5).bind(enable_skill_on_ttl)

A fact is something an Agent knows to be true about it's world.
This could be used to drive agent behavior as an agent learns
more about it's world. Or as a game mechanic.
class WorldFacts(Enum):
  SkyIsBlue: int = auto()
fact = Memory(value=WorldFacts.SkyIsBlue)

Ultimately what am I trying to accomplish?
- Enable replacing the entire memory implementation at the Agent level.
- Enable using different storage mechanisms for memory.
- Enable storing memories with TTLs. 
- Enable running logic when memories expire.
- Easily checking if a memory exists. 
- Support different types of memories (Sense, Recognition, Skill, Fact, States).
- Partitioning of memory (sensory, working, long term)

Key Design Goals:
- Composable: Enable mixing different memory types and storage 
  systems to create rich memory models.
- Functional: Have functions that work on memories. 
  Not memories with methods.
- Bindable: Systems should be able to provide functions to memory banks
  to do what they need. They shouldn't have to cast for specific
  MemoryBank or Memory types.
- Clear: Have memories be strongly typed. Avoid the use of Any.

Memory Functional Operations
- remember
- memorize 
- learn
- recall
- forget
- forget_all
- to_list -> List[Memory]
- assign_ttl

Pieces of the Memory Model
- AgentMemoryModel
  - Top Level Contract. AgentLike had a dependency on this.
  - Injection Point.

- MemoryContainer
  - This is a memory bank. It is a storage container for memories.
  - The type of storage can vary (tree, dict, set, list)
  - Containers should enable applying functions to all the memories
    that they contain.
    MemoryContainer.map(did_recognize).bind(to_list)

- Memory
  - Something an agent can retain in their head.
  - Wraps whatever the memory is. 
  - Should not have a specific contract like Skill or Fact, 
    rather it should be operable using bound functions that 
    systems specify.

Considerations
- Add extensions of List, Set, Dict, Stack, Queue to the FP toolkit. 
  These should implement Monad and Applicative
  These should be useable to create MemoryContainers. 
- Should a memory container be a container directly (e.g. UserList)
  or should it wrap a storage mechanism? At the moment I'm thinking
  it should be a direct storage mechanism that provides a very 
  generic contract (add, remove, apply, bind, map, etc)
"""

A = TypeVar('A')
B = TypeVar('B')

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
  """Represents a memory bank that does nothing."""
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
  """A collection of memory banks."""
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

  def recall(self, label: str) -> Memory:
    """Summon a memory by its label"""
    raise Exception('This does not make sense in the context of a set.')
  
  def forget(self, label: str) -> None:
    """Remove a memory from the memory bank's store.
    This doesn't make sense for a stack based memory bank.
    """
    raise Exception('This does not make sense in the context of a set.')
  
  def forget_all(self, label: str) -> None:
    """Remove all memories from the memory bank's store."""
    self._memory_set.clear()
  
  def memories(self) -> List[Memory]:
    """Return all current memories in the memory bank."""
    return list(self._memory_set)

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
    raise Exception('Does not make sense.')
  
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

class TestAgentMemory:
  def test_extensibility(self) -> None:
    dumb_agent = FakeAgent(memory = NoMemory())
    default_agent = FakeAgent(memory = DefaultAgentMemory())
    push_down_automata = FakeAgent(
      memory = DefaultAgentMemory(
        initial_memory_banks=[StackMemoryBank()]
      )
    )
    three_tier_agent = FakeAgent(
      memory=DefaultAgentMemory(
        initial_memory_banks=[
          FakeSensoryMemoryBank(),
          # FakeWorkingMemoryBank(),
          # FakeLongTermMemory()
        ]
      )
    )

    agent: FakeAgent
    memory_bank: MemoryBankLike