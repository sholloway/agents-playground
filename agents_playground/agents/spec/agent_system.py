from __future__ import annotations
from abc import ABC, abstractclassmethod
from types import SimpleNamespace
from typing import List
from typing_extensions import Self
from more_itertools import consume

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition
from agents_playground.agents.spec.byproduct_store import ByproductStore

class SystemRegistrationError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)
  
class AgentSystem(ABC):
  """
  An agent system is a hierarchy of systems that is scoped to the internal workings
  of an agent. 

  A system can produce one or more byproducts. These byproducts are stored locally 
  in the system's byproducts_store. Byproducts can be passed up or down in the 
  hierarchy. If they are passed up, they must be registered with the parent system.

  The system implementer has the flexibility of adding system logic before or 
  after the system's child processes are ran.
  """
  name: str # The unique name of the system.
  subsystems: SimpleNamespace # Any subsystems this system has.
  byproducts_store: ByproductStore # The collection of byproducts this system products.

  # The list of byproducts this system can produce upwards.
  byproducts_definitions: List[ByproductDefinition] 

  # The list of byproducts this system can produce that does not propagate up.
  # Note: The byproducts_definitions and internal_byproducts_definitions must not 
  # overlap. Each byproduct may only be defined once.
  internal_byproducts_definitions: List[ByproductDefinition] 

  def __init__(
    self, 
    system_name: str, 
    subsystems: SimpleNamespace,
    byproducts_store: ByproductStore,
    byproducts_definitions: List[ByproductDefinition],
    internal_byproducts_definitions: List[ByproductDefinition] 
  ) -> None:
    self.name = system_name
    self.subsystems = subsystems
    self.byproducts_store = byproducts_store
    self.byproducts_definitions = byproducts_definitions
    self.internal_byproducts_definitions = internal_byproducts_definitions
    self.byproducts_store.register_system_byproducts(self.name, byproducts_definitions)
    self.byproducts_store.register_system_byproducts(self.name, internal_byproducts_definitions)
  
  def register_system(
    self, 
    subsystem: AgentSystem
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
    self.byproducts_store.register_subsystem_byproducts(self.name, subsystem.name, subsystem.byproducts_definitions)
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
    parent_byproducts: dict[str, list] = {}
  ) -> None:
    """Orchestrates the processing of the system.

    Args
      - characteristics: The aspects of an agent that can be used as inputs to the system.
      - agent_phase: The specific phase the agent is currently in.
      - byproducts: A generic structure to allow collecting outputs from the various subsystems.
    """
    self._before_subsystems_processed(characteristics, agent_phase, parent_byproducts)
    self._process_subsystems(characteristics, agent_phase)
    self._after_subsystems_processed(characteristics, agent_phase, parent_byproducts) 
    self._collect_byproducts()

  def _process_subsystems(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase
  ) -> None:
    consume(
      map(
        lambda subsystem: subsystem.process(
          characteristics, 
          agent_phase, 
          self.byproducts_store.byproducts
        ), 
        self.subsystems.__dict__.values()
      )
    ) 

  @abstractclassmethod
  def _before_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    parent_byproducts: dict[str, list]
  ) -> None:
    ...
  
  @abstractclassmethod
  def _after_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    parent_byproducts: dict[str, list]
  ) -> None:
    ...
  
  def clear_byproducts(self) -> None:
    """Clears the byproducts of the system. It does NOT clear the subsystem's byproduct stores."""
    self.byproducts_store.clear()

  def _collect_byproducts(self) -> None:
    """
    Collect the registered byproducts of children.

    Note: We're purposefully not passing down a single store to enable systems 
    to have isolated stores. Only byproducts that they register with their parent
    are passed up. After byproducts are collected the subsystem stores are cleared.
    """
    subsystem: AgentSystem
    byproduct_def: ByproductDefinition
    for subsystem in self.subsystems.__dict__.values():
      for byproduct_def in subsystem.byproducts_definitions:
        byproduct = subsystem.byproducts_store.byproducts.get(byproduct_def.name)
        if byproduct and len(byproduct) > 0:
          self.byproducts_store.byproducts[byproduct_def.name].extend(byproduct)
      subsystem.clear_byproducts()
