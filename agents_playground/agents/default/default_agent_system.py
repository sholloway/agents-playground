from types import SimpleNamespace
from agents_playground.agents.spec.agent_system import AgentSystem, ByproductStore

class DefaultAgentSystem(AgentSystem):
  def __init__(
    self, 
    name: str
  ) -> None:
    self.name = name
    self.subsystems = SimpleNamespace()
    self.byproducts_store = ByproductStore()