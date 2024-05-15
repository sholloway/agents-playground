from __future__ import annotations

from agents_playground.agents.memory.agent_memory_model import AgentMemoryModel
from agents_playground.agents.memory.memory import Memory
from agents_playground.agents.memory.memory_container import MemoryContainer

from agents_playground.containers.ttl_store import TTLStore
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


class FakeAgent:
    """Simplified stand in for AgentLike."""

    def __init__(self, memory: AgentMemoryModel) -> None:
        self.memory = memory


class TestAgentMemoryModel:
    def test_building_a_memory_model(self) -> None:
        dumb_agent = FakeAgent(memory=AgentMemoryModel())
        assert len(dumb_agent.memory) == 0

        agent_with_historical_state = FakeAgent(memory=AgentMemoryModel())
        agent_with_historical_state.memory.add(
            "state_memory", MemoryContainer(FPStack[str]())
        )
        assert len(agent_with_historical_state.memory) == 1

        agent_with_tiered_memory = FakeAgent(
            AgentMemoryModel(
                sense_memory=MemoryContainer(FPList[Memory]()),
                working_memory=MemoryContainer(TTLStore[Memory]()),
                long_term_memory=MemoryContainer(FPSet[Memory]()),
            )
        )
        assert len(agent_with_tiered_memory.memory) == 3

    def test_storing_memories(self) -> None:
        agent = FakeAgent(
            AgentMemoryModel(
                {
                    "simple_list": MemoryContainer(FPList[Memory]()),
                    "temp_memories": MemoryContainer(TTLStore[Memory]()),
                }
            )
        )

        # Storing memories in a list.
        assert "simple_list" in agent.memory
        agent.memory["simple_list"].unwrap().append(Memory(123))
        assert agent.memory["simple_list"].unwrap() == FPList([Memory(123)])

        # Storing memories in a TTLStore.
        assert "temp_memories" in agent.memory
        agent.memory["temp_memories"].unwrap().store(item=Memory(789), ttl=5)
        assert Memory(789) in agent.memory["temp_memories"]
