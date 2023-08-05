from __future__ import annotations

from abc import abstractmethod
from math import inf as INFINITY
from typing import Any, Callable, Dict, Generic, List, Protocol, Set, TypeVar, cast

from agents_playground.agents.spec.tick import Tick as FrameTick
from agents_playground.containers.ttl_store import TTLStore

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


"""
What is the contract for a generic monad?
Two main components:
Unit : Take a value and turn it into a Monad
Bind : Take a Monad, apply a function to it and return a new Monad

Monads are contains for values that enable binding functions to 
them.

Is Memory a good fit for a monad?
For a memory, I need a generic container that can bind things like
- expire_on_ttl
- enable_skill_on_ttl

In this case a skill is a memory with a Time To Learn (ttl)
skill = Memory(value=CutWood, ttl=5).bind(enable_skill_on_ttl)

A fact is something an Agent knows to be true about it's world.
This could be used to drive agent behavior as an agent learns
more about it's world. Or as a game mechanic.
class WorldFacts(Enum):
  SkyIsBlue: int = auto()
fact = Memory(value=WorldFacts.SkyIsBlue)
"""

class Monad(Generic[A]):
  def __init__(self, value: A):
    self._value = value

  def bind(self, func: Callable[[A], B]) -> Monad[B]:
    result = func(self._value)
    return Monad[B](result)
    
  def unwrap(self) -> A:
    return self._value

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
    # for agent in (dumb_agent, default_agent, push_down_automata, three_tier_agent):
    #   for memory_bank in agent.memory.memory_banks:
    #     memory_bank.remember() 
  
"""
Ultimately what am I trying to accomplish?
- Allow easily replacing the entire agent's memory model.
- Enable using different storage mechanisms for memory.
- Enable storing memories with TTLs. 
- Enable running logic when memories expire.
- Easily checking if a memory exists. 
- Support different types of memories (senses, facts, skills, states).
- Partitioning of memory (sensory, working, long term)

Design Goals:
- Have memories be strongly typed. Avoid the use of Any.
- Support the ability to have categories of memories.
  Sense, Recognition, Skill, Fact, etc...
- Make it easy to create memory banks with different storage 
  mechanisms.

Current List of Challenges
- What is a memory? 
  Perhaps we need a memory container class. 
  This is to enable things like sensations, recognitions, skills, 
  facts. 
  Monad example: https://github.com/jasondelaat/pymonad/blob/release/pymonad/monad.py

  

  Look at the school of common monads for inspiration.
  Consider generics.

- What is the contract for remembering something?
  The contract for MemoryBankLike doesn't work depending on the 
  internal storage mechanism. Parameters like ttl and label don't 
  make sense for most storage types. 
  This is where I wonder if monads and functors could simplify things.

- How should memory retrieval work? 
  Need to have a generic enough contract to support internal lists, dicts, trees, etc.

- How to deal with multi-storage memory bank like long term memory (memories, skills, knowledge)?
Options
  - Flatten it. Rather than have the hierarchy be Sensory Memory, Working Memory, Long Term Memory
    have it be: Sensory Memory, Working Memory, long term memories, skills, knowledge.
    (I like this approach better.)
  - Use the composite pattern.

- The ttl needs to be universal.
"""