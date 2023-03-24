from types import SimpleNamespace
from agents_playground.agents.spec.agent_system import AgentSystem

class DefaultAgentSystem(AgentSystem):
  def __init__(
    self, 
    name: str, 
    subsystems: SimpleNamespace
  ) -> None:
    self.name = name
    self.subsystems: SimpleNamespace = subsystems