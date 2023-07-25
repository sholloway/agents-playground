from __future__ import annotations
from abc import abstractmethod
from math import inf as INFINITY
from typing import Any, Dict, List, Protocol, cast

from agents_playground.agents.spec.tick import Tick as FrameTick

class Agent:
  """Simplified stand in for AgentLike."""
  def __init__(self, memory: AgentMemoryLike) -> None:
    self.memory = memory

# What is the definition of a memory?
Memory = str
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
  
  def memories(self) -> List[Memory]:
    """Return all current memories in the memory bank."""
    return []

class NoMemoryBank(MemoryBankLike):
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
  A memory bank for a dumb agent that cannot remember anything.
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
  pass

class TestAgentMemory:
  def test_blah(self) -> None:
    dumb_agent = Agent(memory = NoMemory())
    default_agent = Agent(memory = DefaultAgentMemory())
  