from abc import abstractmethod
from typing import Protocol
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics

class AgentActionSelector(Protocol):
  @abstractmethod
  def next_action(
    self, 
    agent_characteristics: AgentCharacteristics, 
    current_action: AgentActionStateLike
  ) -> AgentActionStateLike:
    ...