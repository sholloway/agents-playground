from __future__ import annotations

from abc import abstractmethod
from collections.abc import Collection, Hashable
from math import inf as INFINITY
from typing import Any, Type, cast, Callable, Dict, Generic, List, Protocol, Set, TypeVar

from agents_playground.agents.spec.tick import Tick as FrameTick
from agents_playground.containers.ttl_store import TTLStore
from agents_playground.fp import Bindable, Maybe, Monad, Nothing, Wrappable
from agents_playground.fp.containers import FPCollection, FPDict, FPList, FPSet, FPStack

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


"""
What can be done to a memory?
Remember, forget,...
"""
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
    memory_metadata: Maybe[MemoryMetadata],
    # Having ttl here when it's only used for a few stores seems wasteful and leaky.
    ttl: Maybe[int] 
  ) -> None:
    """
    Create a new instance of a Memory.

    Args:
      core_memory (MemoryValue): The main concept that this memory wraps.
      memory_metadata (Maybe[MemoryMetadata]): An optional piece of metadata that a memory can contain.
      ttl (Maybe[int]): The optional time to live for this memory. 
    """
    self._core_memory = core_memory
    self._memory_metadata = memory_metadata 
    self._ttl = ttl 

  def wrap(
    self, 
    core_memory: MemoryValue
  ) -> 'Memory[MemoryValue, Nothing]':
    return Memory(
      core_memory = core_memory, 
      memory_metadata = Nothing(),
      ttl = Nothing()
    )
  
  @staticmethod
  def instance(core_memory: MemoryValue) -> Memory:
    return Memory(
      core_memory = core_memory, 
      memory_metadata = Nothing(),
      ttl = Nothing()
    )

  def unwrap(self) -> MemoryValue:
    return self._core_memory
  
  def metadata(self) -> Maybe[MemoryMetadata]:
    return self._memory_metadata
  
  def ttl(self) -> Maybe[int]:
    return self._ttl
  
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
    return hash((self._core_memory, self._memory_metadata, self._ttl))
  
class AgentMemoryError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

"""
The design of memory_banks as a dict of FPCollections isn't accomplishing 
what I want. Is the answer to my abstraction challenge more abstraction?

AgentMemoryLike -o< MemoryContainer -->  FPList | FPSet, FPDict | FPTree, TTLStore, etc -> Memory

Ditch FPCollection and have the container classes deal with the container.abc stuff.

MemoryContainer
  - Leverage multi-dispatch on this to enable different types of add methods.


| Storage Type | Add Style | 
|--------------|-----------|
| FPList       | append(item) |
| FPStack      | push(item) |
| FPDict       | store[key] item |
| FPSet        | add(item) |
| TTLStore     | store(item, ttl, tick_action) |

"""
from math import inf as INFINITY
TTL_INFINITY = cast(int, INFINITY)
MemoryContainerStorage = TypeVar("MemoryContainerStorage", FPList, FPStack, FPDict, FPSet, TTLStore)
class MemoryContainer(FrameTick):
  def __init__(self, storage: MemoryContainerStorage) -> None:
    self._storage = storage

  def tick(self) -> None:
    """
    Rather than call item.tick(), should it be a mapped or bound function?
    for item in items:
      item.tick()

    verses

    for item in items:
      tick(item)
    """
    raise NotImplementedError('Need to loop over the items and call tick on them if it has it.')
  
  """
  Perhaps what I'm trying to do isn't reasonable. Some systems expect a TTL and 
  some systems do not.

  The contract for add could just leverage **kargs.

  
  """
  def add(self, memory: Memory, tick_action: Callable, ttl: int = TTL_INFINITY,) -> None:
    # I need my own dispatch method...
    match self._storage:
      case a_list if isinstance(self._storage, FPList):
        cast(FPList, a_list).append(memory)
      case _:
        raise Exception()



class AgentMemoryLike(Protocol):
  memory_banks: FPDict[str, FPCollection[Memory, str]] 

  def register(self, name: str, memory_bank: FPCollection) -> None:
    if name in self.memory_banks:
      raise AgentMemoryError(f'The memory bank {name} is already registered.')
    self.memory_banks[name] = memory_bank

class DefaultAgentMemory(AgentMemoryLike):
  def __init__(
    self, 
    memory_banks:FPDict[str, FPCollection[Memory, str]] | None = None
  ) -> None:
    super().__init__()
    if memory_banks is None:
      self.memory_banks = FPDict()
    else:
      self.memory_banks = memory_banks

class FakeAgent:
  """Simplified stand in for AgentLike."""
  def __init__(self, memory: AgentMemoryLike) -> None:
    self.memory = memory

class TestAgentMemory:
  def test_extensibility(self) -> None:
    """
    Demonstrate swapping out the entire memory system.
    """
    agent_with_no_memory_capacity = FakeAgent(memory=DefaultAgentMemory())
    
    agent_with_simple_memory_capacity = FakeAgent(
      memory = DefaultAgentMemory(
        memory_banks=FPDict({'simple_memory': FPList[Memory]()})
      )
    )
    
    agent_with_tiered_memory_capacity = FakeAgent(
      memory = DefaultAgentMemory(
        memory_banks=FPDict({
          'sense_memory': FPList[Memory](),
          'working_memory': FPSet[Memory](),
          'long_term_memory': FPDict[str, Memory](),
        })
      )
    )

    # The contract for saving a memory.
    # This is different for Lists, Sets, Dicts, etc...
    for agent in ( 
      agent_with_no_memory_capacity, 
      agent_with_simple_memory_capacity, 
      agent_with_tiered_memory_capacity):
      memory_bank: FPCollection
      for memory_bank in agent.memory.memory_banks.values():
        # Note: The metadata here is specified because the FPDict 
        # based memory banks need it. 
        memory_bank.contain(Memory.instance(5), 'remember_5')

    assert len(agent_with_no_memory_capacity.memory.memory_banks) == 0
    assert Memory.instance(5) in agent_with_simple_memory_capacity.memory.memory_banks['simple_memory']
    assert Memory.instance(5) in agent_with_tiered_memory_capacity.memory.memory_banks['sense_memory']
    assert Memory.instance(5) in agent_with_tiered_memory_capacity.memory.memory_banks['working_memory']
    
    assert Memory.instance(5) not in agent_with_tiered_memory_capacity.memory.memory_banks['long_term_memory']
    assert 'remember_5' in agent_with_tiered_memory_capacity.memory.memory_banks['long_term_memory']

  def test_composability(self) -> None:
    """
    Demonstrate enabling mixing different memory types and storage 
    systems to create rich memory models.
    """
    pass 

  def test_functional(self)->None:
    """
    Demonstrate that functions are applied to memories. 
    Not memories with methods.
    """ 
    pass

  def test_bindable(self) -> None:
    """
    Demonstrate that memory banks are bindable. Systems should 
    be able to bind functions memory banks to do what they need.
    They shouldn't have to cast for specific MemoryBank or Memory
    types.
    """
    pass 