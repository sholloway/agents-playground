from __future__ import annotations
from typing import Dict, List, Protocol, Set, Tuple
from agents_playground.agents.spec.agent_memory_spec import (
  AgentMemoryLike,
  Fact, 
  LongTermMemoryLike,
  Memory,
  Relationship,
  Sensation, 
  SensoryMemoryLike,
  Skill, 
  WorkingMemoryLike
)
from agents_playground.containers.ttl_store import TTLStore
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.simulation.tag import Tag

class DefaultSensoryMemory(SensoryMemoryLike):
  def __init__(self) -> None:
    self.memory_store: List[Sensation] = []

  def __repr__(self) -> str:
    return f"""
    Type: {self.__class__.__name__}\n
    Memory Store: {self.memory_store}
    """
  
  def tick(self) -> None:
    return
    

class DefaultWorkingMemory(WorkingMemoryLike):
  def __init__(self) -> None:
    self.recognitions: TTLStore = TTLStore()

  def __repr__(self) -> str:
    return f"""
    Type: {self.__class__.__name__}\n
    Recognitions:
    {self.recognitions}
    """.strip()
  
  def tick(self) -> None:
    self.recognitions.tick()

class DefaultLongTermMemory(LongTermMemoryLike):
  def __init__(self) -> None:
    super().__init__()
    self.memories: Set[Memory]  = set()
    self.skills: Set[Skill]     = set()
    self.knowledge: Set[Fact]   = set()
    self.relationships: Dict[Tag, Relationship] = {}

  def remember(self, memory: Memory) -> None:
    """Make a long term memory."""
    return

  def learn(self, skill: Skill) -> None:
    """Acquire a skill."""
    return

  def memorize(self, fact: Fact) -> None:
    """Remember a fact."""
    return

  def recognize(self, AgentLike) -> Tuple[bool, Relationship]:
    """Does the agent know another agent?"""
    return (True, Relationship())
  
  def __repr__(self) -> str:
    return f"""
    Type: {self.__class__.__name__}\n
    Memories: {self.memories}\n
    Skills: {self.skills}\n
    Knowledge: {self.knowledge}\n
    Relationships: {self.relationships}\n
    """
  
  def tick(self) -> None:
    return

class DefaultAgentMemory(AgentMemoryLike):
  def __init__(
    self, 
    sensory_memory: SensoryMemoryLike, 
    working_memory: WorkingMemoryLike, 
    long_term_memory: LongTermMemoryLike
  ) -> None:
    self.sensory_memory: SensoryMemoryLike    = sensory_memory
    self.working_memory: WorkingMemoryLike	  = working_memory
    self.long_term_memory: LongTermMemoryLike = long_term_memory