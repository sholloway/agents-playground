from typing import Callable, NamedTuple
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.likelihood.coin import Coin

class AgentStateTransitionRule(NamedTuple):
  state: AgentActionStateLike
  transition_to: AgentActionStateLike
  condition: Callable[[AgentCharacteristics], bool]
  likelihood: Coin

