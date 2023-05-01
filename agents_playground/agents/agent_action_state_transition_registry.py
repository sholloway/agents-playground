
from typing import Callable, Dict

from agents_playground.agents.default.default_agent_action_state_rules_set import always_transition
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics

AGENT_ACTION_STATE_TRANSITION_REGISTRY: Dict[str, Callable[[AgentCharacteristics],bool]] = {
  'always_transition': always_transition
}