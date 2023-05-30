from types import SimpleNamespace
from typing import List
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_life_cycle_phase import AgentLifeCyclePhase
from agents_playground.agents.spec.agent_system import AgentSystem, ByproductDefinition, ByproductStore

class DefaultAgentSystem(AgentSystem):
  def __init__(
    self, 
    name: str
  ) -> None:
    super().__init__(
      system_name = name, 
      subsystems = SimpleNamespace(), 
      byproducts_store = ByproductStore(),
      byproducts_definitions = [],
      internal_byproducts_definitions = []
    )

  def _before_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    parent_byproducts: dict[str, list]
  ) -> None:
    return
  
  
  def _after_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    parent_byproducts: dict[str, list]
  ) -> None:
    return

class SystemWithByproducts(AgentSystem):
  def __init__(
    self, 
    name:str, 
    byproduct_defs: List[ByproductDefinition] = [],
    internal_byproduct_defs: List[ByproductDefinition] = []
  ) -> None:
    super().__init__(
      system_name = name, 
      subsystems = SimpleNamespace(), 
      byproducts_store = ByproductStore(),
      byproducts_definitions = byproduct_defs,
      internal_byproducts_definitions = internal_byproduct_defs
    )

  def _before_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    parent_byproducts: dict[str, list]
  ) -> None:
    return
  
  
  def _after_subsystems_processed(
    self, 
    characteristics: AgentCharacteristics, 
    agent_phase: AgentLifeCyclePhase,
    parent_byproducts: dict[str, list]
  ) -> None:
    return