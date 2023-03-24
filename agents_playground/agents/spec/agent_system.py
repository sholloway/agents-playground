from __future__ import annotations

from types import SimpleNamespace
from typing import Protocol
from typing_extensions import Self
from more_itertools import consume

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase

class AgentSystem(Protocol):
  name: str
  subsystems: SimpleNamespace

  def register_system(self, system: AgentSystem) -> Self:
    if not hasattr(self.subsystems, system.name):
      self.subsystems.__setattr__(system.name, system)
    return self 
  
  def process(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    self.before_subsystems_processed(characteristics, agent_phase)
    self.process_subsystems(characteristics, agent_phase)
    self.after_subsystems_processed(characteristics, agent_phase) 

  def process_subsystems(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    consume(map(lambda subsystem: subsystem.process(characteristics, agent_phase), self.subsystems.__dict__.values())) 

  def before_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    return
  
  def after_subsystems_processed(self, characteristics: AgentCharacteristics, agent_phase: AgentLifeCyclePhase) -> None:
    return