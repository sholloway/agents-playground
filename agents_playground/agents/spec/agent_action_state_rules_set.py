from typing import List, Protocol
from more_itertools import first_true
from random import choices

from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_state_transition_rule import (
    AgentStateTransitionRule,
)


class AgentActionStateRulesSet(Protocol):
    rules: List[AgentStateTransitionRule]
    no_rule_resolved: AgentStateTransitionRule

    def evaluate(self, characteristics: AgentCharacteristics) -> AgentActionStateLike:
        """
        Iterate over the list of agent state transition rules and find the next best
        state based on the first rule that has both its condition evaluate to True
        and wins its coin flip.

        Rule Use Cases:
        1. The transition rules are explicit. THIS state transitions to THAT state.
        2. A rule has a condition that must evaluate to true for further consideration.
        3. A rule has an associated probability (i.e. coin flip) that must resolve for further consideration.
        4. A rule multiple possible states associated with it. Each state has a probability. In this case
           both the condition and total rule possibility must be true.
        """
        transition_rule: AgentStateTransitionRule = first_true(
            self.rules,
            default=self.no_rule_resolved,
            pred=lambda rule: rule.condition(characteristics)
            and rule.likelihood.flip(),
        )
        return self._process_transition(transition_rule, characteristics)

    def _process_transition(
        self,
        transition_rule: AgentStateTransitionRule,
        characteristics: AgentCharacteristics,
    ) -> AgentActionStateLike:
        if isinstance(transition_rule.transition_to, tuple):
            # Find the next state using the distribution specified
            # by the cumulative weights.
            return choices(
                population=transition_rule.transition_to,
                cum_weights=transition_rule.choice_weights,
            )[0]
        else:
            return transition_rule.transition_to
