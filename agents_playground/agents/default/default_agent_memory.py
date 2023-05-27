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
from agents_playground.simulation.tag import Tag

class DefaultSensoryMemory(SensoryMemoryLike):
  def __init__(self) -> None:
    self.memory_store: List[Sensation] = []

class DefaultWorkingMemory(WorkingMemoryLike):
  ...

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

class DefaultAgentMemory(AgentMemoryLike):
  def __init__(
    self, 
    sensory_memory: SensoryMemoryLike = DefaultSensoryMemory(), 
    working_memory: WorkingMemoryLike = DefaultWorkingMemory(), 
    long_term_memory: LongTermMemoryLike = DefaultLongTermMemory()
  ) -> None:
    self.sensory_memory: SensoryMemoryLike    = sensory_memory
    self.working_memory: WorkingMemoryLike	  = working_memory
    self.long_term_memory: LongTermMemoryLike = long_term_memory