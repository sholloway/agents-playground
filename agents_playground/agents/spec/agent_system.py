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


  """
  TODO: Can we declare a system's byproducts if any?
  """
  def register_system(self, system: AgentSystem) -> Self:
    if not hasattr(self.subsystems, system.name):
      self.subsystems.__setattr__(system.name, system)
    return self 
  
  def process(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase, 
    byproducts: SimpleNamespace
  ) -> None:
    """Orchestrates the processing of the system.
    
    Args
      - characteristics: The aspects of an agent that can be used as inputs to the system.
      - agent_phase: The specific phase the agent is currently in.
      - byproducts: A generic structure to allow collecting outputs from the various subsystems.
    """
    self.before_subsystems_processed(characteristics, agent_phase, byproducts)
    self.process_subsystems(characteristics, agent_phase, byproducts)
    self.after_subsystems_processed(characteristics, agent_phase, byproducts) 

  def process_subsystems(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    byproducts: SimpleNamespace
  ) -> None:
    consume(
      map(lambda subsystem: subsystem.process(characteristics, agent_phase, byproducts), 
          self.subsystems.__dict__.values())
    ) 

  def before_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    byproducts: SimpleNamespace
  ) -> None:
    return
  
  def after_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    byproducts: SimpleNamespace
  ) -> None:
    return