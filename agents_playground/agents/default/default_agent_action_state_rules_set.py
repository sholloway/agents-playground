from typing import List
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_action_state_rules_set import AgentActionStateRulesSet
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_state_transition_rule import AgentStateTransitionRule
from agents_playground.likelihood.weighted_coin import SureThing

def always_transition(characteristics: AgentCharacteristics) -> bool:
  return True

class DefaultAgentActionStateRulesSet(AgentActionStateRulesSet):
  def __init__(
    self, 
    rules: List[AgentStateTransitionRule], 
    default_state: AgentActionStateLike) -> None:
    self.rules = rules
    self.no_rule_resolved = AgentStateTransitionRule(
      state = NamedAgentActionState(name = 'NONE_AGENT_ACTION_STATE'),
      transition_to = default_state,
      condition = always_transition, 
      likelihood = SureThing(),
      choice_weights = (0.0,)
    )