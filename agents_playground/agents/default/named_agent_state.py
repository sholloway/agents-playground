from agents_playground.agents.spec.agent_state_spec import AgentActionStateLike

class NamedAgentActionState(AgentActionStateLike):
  def __init__(self, name: str) -> None:
    self.name = name

  def __eq__(self, other: object) -> bool:
    if hasattr(other, 'name'):
      return self.name.__eq__(other.name) # type: ignore
    else:
      return False
    
  def __hash__(self) -> int:
    return hash(self.name)