
from typing import Protocol, TypeVar

import agents_playground.agents.memory.collections as memory_stores
from agents_playground.agents.memory.memory_container import MemoryContainer

# KT = TypeVar("KT")
# MV = TypeVar("MV")
class AgentMemoryLike(memory_stores.MutableMapping[str, MemoryContainer], Protocol):
  def add(self, key: str, container: MemoryContainer) -> None: ...