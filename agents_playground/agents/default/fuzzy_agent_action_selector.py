from typing import List

from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_action_state_rules_set import (
    AgentActionStateRulesSet,
)
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.funcs import map_get_or_raise


class FuzzyAgentActionSelector(AgentActionSelector):
    def __init__(
        self, state_map: dict[AgentActionStateLike, AgentActionStateRulesSet] = {}
    ) -> None:
        self._state_map: dict[AgentActionStateLike, AgentActionStateRulesSet] = (
            state_map
        )

    def next_action(
        self,
        characteristics: AgentCharacteristics,
        current_action: AgentActionStateLike,
    ) -> AgentActionStateLike:
        rule: AgentActionStateRulesSet = map_get_or_raise(
            self._state_map,
            current_action,
            Exception(
                f"No AgentActionStateRulesSet mapped to state f{current_action.name}."
            ),
        )
        return rule.evaluate(characteristics)
