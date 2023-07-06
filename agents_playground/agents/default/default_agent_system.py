from types import SimpleNamespace
from typing import Dict, List
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_system import AgentSystem, ByproductDefinition, ByproductStore
from agents_playground.simulation.tag import Tag

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

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, AgentLike]) -> None:
    return
  
  def _before_subsystems_processed_post_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, AgentLike]) -> None:
    return
  
  def _after_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, AgentLike]) -> None:
    return
  
  def _after_subsystems_processed_post_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, AgentLike]) -> None:
    return
  
  def __repr__(self) -> str:
    return f"""
    {self.__class__.__name__}
    """.strip()

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

  def _before_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, AgentLike]) -> None:
    return
  
  def _before_subsystems_processed_post_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, AgentLike]) -> None:
    return
  
  def _after_subsystems_processed_pre_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, AgentLike]) -> None:
    return
  
  def _after_subsystems_processed_post_state_change(
    self, 
    characteristics: AgentCharacteristics, 
    parent_byproducts: Dict[str, List],
    other_agents: Dict[Tag, AgentLike]) -> None:
    return