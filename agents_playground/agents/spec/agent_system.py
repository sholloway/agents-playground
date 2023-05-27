from __future__ import annotations
from types import SimpleNamespace
from typing import List, NamedTuple, Protocol, Type
from typing_extensions import Self
from more_itertools import consume

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase

class SystemRegistrationError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class ByproductDefinition(NamedTuple):
  name: str
  type: type

class ByproductRegistrationError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class ByproductStore:
  """
  Responsible for storing the outputs of systems.
  """
  def __init__(self) -> None:
    self._byproducts: dict[str, list] = {}
    self._registered_byproducts: dict[str, ByproductDefinition] = {}

  @property
  def byproducts(self) -> dict[str, list]:
    return self._byproducts

  def register(
    self, 
    system: AgentSystem,
    subsystem: AgentSystem, 
    possible_byproducts: List[ByproductDefinition]
  ) -> None:
    """
    Registers byproducts that can be collected.

    Args:
      - system: The system that the subsystem is being added to.
      - subsystem: The subsystem that can produce the byproducts.
      - possible_byproducts: The list of byproducts that the subsystem may produce.
    """
    byproduct_def: ByproductDefinition
    for byproduct_def in possible_byproducts:
      if not byproduct_def.name in self._byproducts:
        self._byproducts[byproduct_def.name] = []
        self._registered_byproducts[byproduct_def.name] = byproduct_def
      elif byproduct_def.name in self._registered_byproducts and \
        self._registered_byproducts[byproduct_def.name].type != byproduct_def.type:
        error_msg = f"""
        Error registering system byproducts.
        The system {system.name} attempted to registers subsystem {subsystem.name} with byproduct {byproduct_def.name} of type {byproduct_def.type}.
        However, byproduct {byproduct_def.name} is already registered with type {self._registered_byproducts[byproduct_def.name].type}.
        Byproducts may not have multiple types.
        """
        raise ByproductRegistrationError(error_msg)
      
  

class AgentSystem(Protocol):
  name: str
  subsystems: SimpleNamespace
  byproducts_store: ByproductStore

  def register_system(
    self, 
    subsystem: AgentSystem, 
    possible_byproducts: List[ByproductDefinition] = []
  ) -> Self:
    """
    Add a subsystem. 

    Args:
      - subsystem: The subsystem to add to this system.
      - possible_byproducts: The possible outputs from this system. 
        Note: Multiple systems may output the same byproduct. In that case, 
        they share the same List in the byproducts namespace.
    """
    self._register_system(subsystem)
    self.byproducts_store.register(self, subsystem, possible_byproducts)
    return self 
  
  def _register_system(self,subsystem: AgentSystem) -> None:
    if hasattr(self.subsystems, subsystem.name):
      error_msg =f"""
      Error registering subsystem.
      The system {self.name} attempted to register subsystem {subsystem.name}, 
      however another system was already registered with the same name.
      {self.subsystems}
      """
      raise SystemRegistrationError(error_msg)
    else:
      self.subsystems.__setattr__(subsystem.name, subsystem)
  
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