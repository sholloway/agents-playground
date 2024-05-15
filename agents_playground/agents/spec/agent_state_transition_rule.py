from typing import Callable, NamedTuple, Tuple
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike

from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.likelihood.coin import Coin


class AgentStateTransitionRule(NamedTuple):
    state: AgentActionStateLike
    transition_to: AgentActionStateLike | Tuple[AgentActionStateLike, ...]
    condition: Callable[[AgentCharacteristics], bool]
    likelihood: Coin
    choice_weights: Tuple[float, ...]
