from typing import List, Protocol
from more_itertools import first_true

from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_state_transition_rule import AgentStateTransitionRule
  
class AgentActionStateRulesSet(Protocol):
  rules: List[AgentStateTransitionRule]
  no_rule_resolved: AgentStateTransitionRule

  def evaluate(self, characteristics: AgentCharacteristics) -> AgentActionStateLike:
    """
    Iterate over the list of agent state transition rules and find the next best 
    state based on the first rule that has both its condition evaluate to True 
    and wins its coin flip.
    """
    transition_rule: AgentStateTransitionRule = first_true(
      self.rules, 
      default = self.no_rule_resolved,
      pred = lambda rule: rule.condition(characteristics) and rule.likelihood.flip())
    return transition_rule.transition_to 