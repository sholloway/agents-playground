from types import SimpleNamespace
from typing import Dict, List
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_system import AgentSystemLike, ByproductDefinition, ByproductStore
from agents_playground.simulation.tag import Tag

class DefaultAgentSystem(AgentSystemLike):
  def __init__(
    self, 
    name: str
  ) -> None:
    super().__init__()
    self.name = name
    self.subsystems = SimpleNamespace()
    self.byproducts_store = ByproductStore()
    self.byproducts_definitions = []
    self.internal_byproducts_definitions = []
    self.byproducts_store.register_system_byproducts(self.name, self.byproducts_definitions)
    self.byproducts_store.register_system_byproducts(self.name, self.internal_byproducts_definitions)

class SystemWithByproducts(AgentSystemLike):
  def __init__(
    self, 
    name:str, 
    byproduct_defs: List[ByproductDefinition] = [],
    internal_byproduct_defs: List[ByproductDefinition] = []
  ) -> None:
    super().__init__()
    self.name = name
    self.subsystems = SimpleNamespace()
    self.byproducts_store = ByproductStore()
    self.byproducts_definitions = byproduct_defs
    self.internal_byproducts_definitions = internal_byproduct_defs
    self.byproducts_store.register_system_byproducts(self.name, self.byproducts_definitions)
    self.byproducts_store.register_system_byproducts(self.name, self.internal_byproducts_definitions)
