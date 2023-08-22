
from typing import Protocol, TypeVar

import agents_playground.agents.memory.collections as memory_stores
from agents_playground.agents.memory.memory_container import MemoryContainer
from agents_playground.fp.containers import FPDict

class AgentMemoryLike(FPDict[str, MemoryContainer]):
  def add(self, key: str, container: MemoryContainer) -> None: ...