from __future__ import annotations
from abc import ABC, abstractmethod
from types import SimpleNamespace
from typing import Any, Dict, List, Protocol
from typing_extensions import Self
from more_itertools import consume

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.byproduct_definition import ByproductDefinition
from agents_playground.agents.spec.byproduct_store import ByproductStore
import agents_playground.agents.spec.agent_spec as agent_spec
from agents_playground.simulation.tag import Tag

class SystemRegistrationError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class SystemProcessingError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class SystemMemoryError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)
  
class AgentSystemLike(Protocol):
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
  byproducts_store: ByproductStore # The collection of byproducts this system produces.

  # The list of byproducts this system can produce upwards.
  byproducts_definitions: List[ByproductDefinition] 

  # The list of byproducts this system can produce that does not propagate up.
  # Note: The byproducts_definitions and internal_byproducts_definitions must not 
  # overlap. Each byproduct may only be defined once.
  internal_byproducts_definitions: List[ByproductDefinition] 
  
  def register_system(
    self, 
    subsystem: AgentSystemLike
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
  
  def _register_system(self,subsystem: AgentSystemLike) -> None:
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
    other_agents: Dict[Tag, agent_spec.AgentLike],
    parent_byproducts: dict[str, list] = {}
  ) -> None:
    """Orchestrates the processing of the system.

    Args
      - characteristics: The aspects of an agent that can be used as inputs to the system.
      - agent_phase: The specific phase the agent is currently in.
      - byproducts: A generic structure to allow collecting outputs from the various subsystems.
    """
    self._before_subsystems_processed(characteristics, agent_phase, parent_byproducts, other_agents)
    self._process_subsystems(characteristics, agent_phase, other_agents)
    self._after_subsystems_processed(characteristics, agent_phase, parent_byproducts, other_agents) 
    self._collect_byproducts_from_subsystems()

  def _process_subsystems(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase, 
    other_agents: Dict[Tag, agent_spec.AgentLike]
  ) -> None:
    consume(
      map(
        lambda subsystem: subsystem.process(
          characteristics, 
          agent_phase, 
          other_agents,
          self.byproducts_store.byproducts
        ), 
        self.subsystems.__dict__.values()
      )
    ) 

  def _before_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, agent_spec.AgentLike]
  ) -> None:
    match agent_phase:
      case agent_phase.PRE_STATE_CHANGE:
        self._before_subsystems_processed_pre_state_change(characteristics, parent_byproducts, other_agents)
      case agent_phase.POST_STATE_CHANGE:
        self._before_subsystems_processed_post_state_change(characteristics, parent_byproducts, other_agents)
      case _:
        error_msg = f"""
        System Processing Error
        The system {self.name} encountered an error in the _before_subsystems_processed() method.
        Unknown AgentLifeCyclePhase {agent_phase}. 
        """
        raise SystemProcessingError(error_msg)
      
  def _after_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, agent_spec.AgentLike]
  ) -> None:
    match agent_phase:
      case agent_phase.PRE_STATE_CHANGE:
        self._after_subsystems_processed_pre_state_change(characteristics, parent_byproducts, other_agents)
      case agent_phase.POST_STATE_CHANGE:
        self._after_subsystems_processed_post_state_change(characteristics, parent_byproducts, other_agents)
      case _:
        error_msg = f"""
        System Processing Error
        The system {self.name} encountered an error in the _after_subsystems_processed() method.
        Unknown AgentLifeCyclePhase {agent_phase}. 
        """
        raise SystemProcessingError(error_msg)
  
  def clear_byproducts(self) -> None:
    """Clears the byproducts of the system. It does NOT clear the subsystem's byproduct stores."""
    self.byproducts_store.clear()

  def _collect_byproducts_from_subsystems(self) -> None:
    """
    Collect the registered byproducts of children.

    Note: We're purposefully not passing down a single store to enable systems 
    to have isolated stores. Only byproducts that they register with their parent
    are passed up. After byproducts are collected the subsystem stores are cleared.
    """
    subsystem: AgentSystemLike
    byproduct_def: ByproductDefinition

    for subsystem in self.subsystems.__dict__.values():
      for byproduct_def in subsystem.byproducts_definitions:
        byproduct = subsystem.byproducts_store.byproducts.get(byproduct_def.name, [])
        self.byproducts_store.byproducts[byproduct_def.name].extend(byproduct)
      subsystem.clear_byproducts()
    
  def _push_byproducts_to_parent(self, parent_byproducts: Dict[str, List]) -> None:
    """
    A convenience method that pushes the active system's registered byproducts to 
    the parent system. This is intended to be used in systems that cannot wait for 
    _collect_byproducts_from_subsystems to be run by their parent.

    It does not collect the subsystem byproducts to allow for more flexibility in 
    child systems.
    """
    for byproduct_def in self.byproducts_definitions:
      byproduct = self.byproducts_store.byproducts.get(byproduct_def.name, [])
      if byproduct_def.name in parent_byproducts:
        self.byproducts_store.byproducts.get(byproduct_def.name)
        parent_byproducts[byproduct_def.name].extend(byproduct)
      else:
        error_msg = f"""
        System Processing Error
        The system {self.name} had an error in its life cycle step _after_subsystems_processed_pre_state_change().
        The external byproduct definition {byproduct_def.name} was not registered with the parent system.
        """
        raise SystemProcessingError(error_msg)

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List], 
    other_agents: Dict[Tag, agent_spec.AgentLike]) -> None:
    """
    An optional hook for doing work before the agent's state changes.
    """
    return
  
  def _before_subsystems_processed_post_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List], 
    other_agents: Dict[Tag, agent_spec.AgentLike]) -> None:
    """
    An optional hook for doing work after the agent's state changes.
    """
    return
  
  def _after_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, agent_spec.AgentLike]) -> None:
    """
    An optional hook for doing work before the agent's state changes.
    """
    return
  
  def _after_subsystems_processed_post_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, agent_spec.AgentLike]) -> None:
    """
    An optional hook for doing work after the agent's state changes.
    """
    return
