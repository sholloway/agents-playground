from agents_playground.agents.spec.agent_state_spec import AgentActionStateLike

class NamedAgentState(AgentActionStateLike):
  def __init__(self, name: str) -> None:
    self.name = name