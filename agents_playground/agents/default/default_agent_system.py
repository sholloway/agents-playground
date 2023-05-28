from types import SimpleNamespace
from typing import List
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