from __future__ import annotations

from abc import abstractmethod
from collections.abc import Collection, Hashable, MutableMapping
from math import inf as INFINITY
from typing import Any, Iterator, Type, cast, Callable, Dict, Generic, List, Protocol, Set, TypeVar

from agents_playground.agents.spec.tick import Tick as FrameTick
from agents_playground.containers.ttl_store import TTLStore
from agents_playground.fp import Bindable, Maybe, Monad, Nothing, Something, Wrappable
from agents_playground.fp.containers import FPDict, FPList, FPSet, FPStack

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
- Enable storing memories with TTLs. Is this optional?
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
  - Injection Point. Different agents can have different memory models.
  - Represents an agent's mind. What they're able to remember. 
  - The AgentMemoryModel is responsible for:
    - Being a clean injection seam.
    - Organizing the various memory containers. 
    - Dispatching a memory command to the appropriate memory container?

- MemoryContainer
  - This is a memory bank. It is a storage container for memories.
  - The type of storage can vary (tree, dict, set, list)
  - Containers should enable applying functions to all the memories
    that they contain.
    MemoryContainer.map(did_recognize).bind(to_list)
  - The MemoryContainer is responsible for:
    - Wraps the in memory storage of a group of memories. 
    - Elevates base level primitives to be in the domain of memories.

- Memory
  - Something an agent can retain in their head.
  - Wraps whatever the memory is. 
  - Should not have a specific contract like Skill or Fact, 
    rather it should be operable using bound functions that 
    systems specify.
  - The Memory class is responsible for:  
    - ?

Considerations
- Add extensions of List, Set, Dict, Stack, Queue to the FP toolkit. 
  These should implement Monad and Applicative
  These should be useable to create MemoryContainers. 
- Should a memory container be a container directly (e.g. UserList)
  or should it wrap a storage mechanism? At the moment I'm thinking
  it should be a direct storage mechanism that provides a very 
  generic contract (add, remove, apply, bind, map, etc)


The design of memory_banks as a dict of FPCollections isn't accomplishing 
what I want. Is the answer to my abstraction challenge more abstraction?

Ditch FPCollection and have the container classes deal with the container.abc stuff.

AgentLike --> AgentMemoryLike --< MemoryContainer -->  FPList | FPSet, FPDict | FPTree, TTLStore -> Memory


# Implement the abc MutableMapping to make it so clients aren't 
# interacting with the internal storage on the memory model.
class AgentMemoryModel(MutableMapping[str, Maybe]): 
  def add(self, memories_container: MemoryContainer, key: str) -> None
  def remove(self, key: str) -> Maybe[MemoryContainer]
  def tick() -> None

  # Dispatching to memory containers ideas
  def map(self, container_name: str, func: Callable[[MemoryContainer], Result]) -> Functor[Result]
  def collect(self, container_name: str, func: Callable[[MemoryContainer], Any]) -> FPList[Result]

  def dispatch(self, container_name: str, func_name: str, args) -> None
    # calls a method on the container if it exists and passes in the provided args.
    # This seems rather hacky.

  # MutableMapping methods
  def __getitem__(...) 
  def __setitem__(...)
  def __delitem__(...)
  def __iter__(...)
  def __len__(...)

| Storage Type | Add Style | 
|--------------|-----------|
| FPList       | append(item) |
| FPStack      | push(item) |
| FPDict       | store[key] item |
| FPSet        | add(item) |
| TTLStore     | store(item, ttl, tick_action) |

Generic contract?
def store(item, metadata) -> None:
  ... 

The issue with this is what's the type for metadata? FPDict[dict, Any]? 

vs multiple methods
def store(self, item) -> None
def store_with_metadata(self, item, metadata: dict[str, Any]) -> None
def store_with_countdown(self, item, metadata: dict[str, Any], ttl: int, tick_action: Callable, expire_action: Callable)
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

    The thing with using the FP style containers for memory is that
    changing the wrapped values shouldn't really happen. They should
    be using pure functions and immutable items.
    """
    raise NotImplementedError('Need to loop over the items and call tick on them if it has it.')
  
  """
  Perhaps what I'm trying to do isn't reasonable. Some systems expect a TTL and 
  some systems do not.

  Could the contract for add could just leverage **kargs? Yuck...  

  I'm trying to avoid including the multimethod 3rd party library. 
  """
  def add(self, memory: Memory, tick_action: Callable, ttl: int = TTL_INFINITY) -> None:
    # I need my own dispatch method...
    match self._storage:
      case a_list if isinstance(self._storage, FPList):
        cast(FPList, a_list).append(memory)
      case _:
        raise Exception()

class AgentMemoryModelError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class AgentMemoryModel(MutableMapping[str, MemoryContainer]): 
  """
  Represents an agent's mind. What they're able to remember. 
  """
  def __init__(self) -> None:
    super().__init__()
    self._data: FPDict[str, MemoryContainer] = FPDict()

  def __getitem__(self, key: str) -> MemoryContainer:
    """
    Provide the ability to fetch an item by it's key.
    Raises a KeyError if nothing is found. 

    Examples:
      >>> memory_model['sense_memory']
    """
    return self._data[key]
  
  def get_maybe(self, key: str) -> Maybe[MemoryContainer]:
    """A safe way to find a container.

    Returns:
      Maybe[MemoryContainer]: Wraps the result in a Maybe. 

    Examples:
      >>> state_memory: Maybe[MemoryContainer] = memory_model.get_maybe('sense_memory')
    """
    return Something(self._data[key]) if key in self._data else Nothing()
    
  def __setitem__(self, key: str, container: MemoryContainer) -> None:
    """Enables setting a container.
    
    Args:
      key (str): The unique identifier for the container.
      container (MemoryContainer): The storage mechanism for a group of memories.

    Examples:
      >>> memory_model['long_term_memory'] = FPSet[Memory]().
    
    """
    self._data[key] = container

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
    """Notifies each memory container that the simulation has advanced one frame."""
    container: MemoryContainer
    for container in self._data.values():
      if(hasattr(container, 'tick')):
        container.tick()

class FakeAgent:
  """Simplified stand in for AgentLike."""
  def __init__(self, memory: AgentMemoryModel) -> None:
    self.memory = memory

class TestAgentMemory:
  def test_nothing_at_the_moment(self) -> None:
    assert True