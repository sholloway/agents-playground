from __future__ import annotations
from typing import List, Protocol
from agents_playground.agents.spec.agent_memory_spec import (
  AgentMemoryLike, 
  LongTermMemoryLike,
  Sensation, 
  SensoryMemoryLike, 
  WorkingMemoryLike
)

class DefaultSensoryMemory(SensoryMemoryLike):
  def __init__(self) -> None:
    self.memory_store: List[Sensation] = []

class DefaultWorkingMemory(WorkingMemoryLike):
  ...

class DefaultLongTermMemory(LongTermMemoryLike):
  ...

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