from __future__ import annotations
from abc import ABC
from types import SimpleNamespace
from typing import Any, List, NamedTuple, Protocol, Type
from typing_extensions import Self
from more_itertools import consume

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase

class ByproductStorageError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

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

  def register_system_byproducts(self, system: AgentSystem, byproduct_defs: List[ByproductDefinition]) -> None:
    byproduct_def: ByproductDefinition
    for byproduct_def in byproduct_defs:
      if not byproduct_def.name in self.byproducts:
        self._byproducts[byproduct_def.name] = []
        self._registered_byproducts[byproduct_def.name] = byproduct_def
      elif (byproduct_def.name in self._registered_byproducts) and \
        (self._registered_byproducts[byproduct_def.name].type != byproduct_def.type):
        error_msg = f"""
        Error registering system byproduct.
        The system {system.name} attempted to register the byproduct {byproduct_def.name} for it's internal
        byproduct store. However the byproduct was already registered there with a different type.
        """
        raise ByproductRegistrationError(error_msg)

  def register_subsystem_byproducts(
    self, 
    system: AgentSystem,
    subsystem: AgentSystem
  ) -> None:
    """
    Registers byproducts that can be collected.

    Args:
      - system: The system that the subsystem is being added to.
      - subsystem: The subsystem that can produce the byproducts.
      - possible_byproducts: The list of byproducts that the subsystem may produce.
    """
    byproduct_def: ByproductDefinition
    for byproduct_def in subsystem.byproducts_definitions:
      if not byproduct_def.name in self._byproducts:
        self._byproducts[byproduct_def.name] = []
        self._registered_byproducts[byproduct_def.name] = byproduct_def
      elif (byproduct_def.name in self._registered_byproducts) and \
        (self._registered_byproducts[byproduct_def.name].type != byproduct_def.type):
        error_msg = f"""
        Error registering subsystem byproducts.
        The system {system.name} attempted to registers subsystem {subsystem.name} with byproduct {byproduct_def.name} of type {byproduct_def.type}.
        However, byproduct {byproduct_def.name} is already registered with type {self._registered_byproducts[byproduct_def.name].type}.
        Byproducts may not have multiple types.
        """
        raise ByproductRegistrationError(error_msg)
      
  def store(self, system: AgentSystem, byproduct_name: str, value: Any) -> None:
    if byproduct_name in self.byproducts:
      self.byproducts[byproduct_name].append(value)
    else:
      error_msg=f"""
      Byproduct Storage Error
      The system {system.name} attempted to store the value {value} byproduct {byproduct_name}
      in its internal byproduct store.
      However, there was no byproduct registered with the name {byproduct_name}.
      """
      raise ByproductStorageError(error_msg)

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
    self.byproducts_store.register_system_byproducts(self, byproducts_definitions)
    self.byproducts_store.register_system_byproducts(self, internal_byproducts_definitions)
  
  def register_system(
    self, 
    subsystem: AgentSystem,
    
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
    self.byproducts_store.register_subsystem_byproducts(self, subsystem)
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
    agent_phase: AgentLifeCyclePhase
  ) -> None:
    """Orchestrates the processing of the system.

    Args
      - characteristics: The aspects of an agent that can be used as inputs to the system.
      - agent_phase: The specific phase the agent is currently in.
      - byproducts: A generic structure to allow collecting outputs from the various subsystems.
    """
    self.before_subsystems_processed(characteristics, agent_phase)
    self.process_subsystems(characteristics, agent_phase)
    self.after_subsystems_processed(characteristics, agent_phase) 
    self.collect_byproducts()

  def process_subsystems(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,

  ) -> None:
    consume(
      map(lambda subsystem: subsystem.process(characteristics, agent_phase), 
          self.subsystems.__dict__.values())
    ) 

  def before_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase
  ) -> None:
    return
  
  def after_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase
  ) -> None:
    return
  
  def collect_byproducts(self) -> None:
    """
    Collect the registered byproducts of children.

    Note: We're purposefully not passing down a single store to enable systems 
    to have isolated stores. Only byproducts that they register with their parent
    are passed up.
    """
    subsystem: AgentSystem
    byproduct_def: ByproductDefinition
    for subsystem in self.subsystems.__dict__.values():
      for byproduct_def in subsystem.byproducts_definitions:
        byproduct = subsystem.byproducts_store.byproducts.get(byproduct_def.name)
        if byproduct and len(byproduct) > 0:
          self.byproducts_store.byproducts[byproduct_def.name].extend(byproduct)
