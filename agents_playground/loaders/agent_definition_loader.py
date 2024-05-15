from dataclasses import dataclass
from typing import Any

from agents_playground.agents.default.default_agent_action_state_rules_set import (
    DefaultAgentActionStateRulesSet,
)
from agents_playground.agents.default.fuzzy_agent_action_selector import (
    FuzzyAgentActionSelector,
)
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_action_state_rules_set import (
    AgentActionStateRulesSet,
)
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_state_transition_rule import (
    AgentStateTransitionRule,
)
from agents_playground.fp import Maybe, wrap_field_as_maybe
from agents_playground.legacy.scene.parsers.types import TransitionCondition
from agents_playground.likelihood.coin import Coin
from agents_playground.likelihood.coin_registry import COIN_REGISTRY, CoinType
from agents_playground.loaders import JSONFileLoader, search_directories
from agents_playground.spatial.vector import vector
from agents_playground.spatial.frustum import Frustum, Frustum3d
from agents_playground.spatial.vector.vector import Vector

AGENT_DEF_SCHEMA_PATH = "agents_playground/agents/file/agent_def.schema.json"


class AgentDefinitionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


@dataclass
class ModelTransformation:
    translation: Vector
    rotation: Vector
    scale: Vector


@dataclass
class FsmAgentStateModel:
    agent_states: dict[str, AgentActionStateLike]
    initial_agent_state: AgentActionStateLike
    state_transition_map: AgentActionSelector

    def __post_init__(self) -> None:
        # Handle when the instance has been loaded by parsing a JSON file and
        # needs to be converted to it's proper type.
        if isinstance(self.agent_states, list):
            # Convert a list of strings to dict[str, AgentActionStateLike].
            self.agent_states = {
                state_name: NamedAgentActionState(state_name)
                for state_name in self.agent_states
            }

        if isinstance(self.initial_agent_state, str):
            # Convert a string to AgentActionStateLike
            self.initial_agent_state = NamedAgentActionState(
                name=self.initial_agent_state
            )

        if isinstance(self.state_transition_map, list):
            # Convert list of dicts to an AgentActionSelector instance.
            self.state_transition_map = self._build_agent_action_selector(
                self.state_transition_map
            )

    def _verify_transition_rules(self, transition_rules: list[dict[str, Any]]) -> None:
        # 1. Collect the names of every state that is referred to in all the transition rules.
        states_referred_to: set[str] = set()
        for transition_rule in transition_rules:
            states_referred_to.add(transition_rule["current_state"])
            states_referred_to.update(transition_rule["transitions_to"])

        # 2. Verify that all states are accounted for.
        registered_states = self.agent_states.keys()
        unregistered_states: set[str] = states_referred_to.difference(registered_states)
        if len(unregistered_states) > 0:
            msg = (
                "Invalid AgentDefinition file.\n",
                f"State transition rules refers to unknown state(s) {unregistered_states}.\n",
            )
            raise AgentDefinitionException(msg)

    def _build_agent_action_selector(
        self, transition_rules: list[dict[str, Any]]
    ) -> AgentActionSelector:
        # 1. Make sure that the rules are all ok.
        self._verify_transition_rules(transition_rules)

        # 2. Build the set of state transition rules.
        rule_set: AgentActionStateRulesSet = self._build_state_transition_rules_set(
            transition_rules
        )

        # 3. Construct the map of rule evaluation sets for each state.
        state_map: dict[AgentActionStateLike, AgentActionStateRulesSet] = (
            self._build_map_of_state_transition_rules(rule_set)
        )

        return FuzzyAgentActionSelector(state_map=state_map)

    def _build_state_transition_rules_set(
        self, transition_rules: list[dict[str, Any]]
    ) -> AgentActionStateRulesSet:
        rules_list: list[AgentStateTransitionRule] = []

        for transition_rule in transition_rules:
            # 1. Get the current state
            current_state_name = transition_rule["current_state"]
            current_state: AgentActionStateLike = self.agent_states[current_state_name]

            # 2. Collect the states that can be transitioned to.
            possible_future_states: tuple[AgentActionStateLike, ...] = tuple(
                [
                    self.agent_states[state_name]
                    for state_name in transition_rule["transitions_to"]
                ]
            )

            # 3. Build the transition condition.
            transition_condition: TransitionCondition = lambda i: True
            coin: Coin = COIN_REGISTRY[CoinType.ALWAYS_HEADS]
            chances: tuple[float, ...] = tuple()
            rules_list.append(
                AgentStateTransitionRule(
                    state=current_state,
                    transition_to=possible_future_states,
                    condition=transition_condition,
                    likelihood=coin,
                    choice_weights=chances,
                )
            )

        return DefaultAgentActionStateRulesSet(
            rules=rules_list, default_state=self.initial_agent_state
        )

    def _build_map_of_state_transition_rules(
        self, rule_set: AgentActionStateRulesSet
    ) -> dict[AgentActionStateLike, AgentActionStateRulesSet]:
        state_map: dict[AgentActionStateLike, AgentActionStateRulesSet] = {}

        # Determine the default state to use if none is found when evaluating the rule set.
        default_state: AgentActionStateLike
        if isinstance(rule_set.no_rule_resolved.transition_to, tuple):
            default_state = rule_set.no_rule_resolved.transition_to[0]
        else:
            default_state = rule_set.no_rule_resolved.transition_to

        # Find each unique state that has associated transition rules.
        agent_states_with_rules: set[AgentActionStateLike] = set(
            [rule.state for rule in rule_set.rules]
        )

        # For each unique state, use filter to get all the rules for that.
        # Then, Create a new AgentActionStateRulesSet that has just those rules and default state.
        for agent_state in agent_states_with_rules:
            state_specific_rules: list[AgentStateTransitionRule] = [
                rule for rule in rule_set.rules if rule.state == agent_state
            ]
            state_map[agent_state] = DefaultAgentActionStateRulesSet(
                state_specific_rules, default_state
            )

        return state_map


@dataclass
class AgentDefinition:
    agent_model: str  # TODO: Figure out where/when to load the model.
    model_transformation: ModelTransformation
    view_frustum: Frustum
    agent_state_model: Maybe[FsmAgentStateModel]
    alias: str = ""

    def __post_init__(self) -> None:
        """
        Handle converting from JSON populated members to their correct objects.
        """
        if isinstance(self.model_transformation, dict):
            self.model_transformation = ModelTransformation(
                translation=vector(*self.model_transformation["translation"]),
                rotation=vector(*self.model_transformation["rotation"]),
                scale=vector(*self.model_transformation["scale"]),
            )

        if isinstance(self.view_frustum, dict):
            self.view_frustum = Frustum3d(
                near_plane_depth=self.view_frustum["near_plane"],
                depth_of_field=self.view_frustum["far_plane"],
                field_of_view=self.view_frustum["vertical_field_of_view"],
            )  # type: ignore

        wrap_field_as_maybe(
            self, "agent_state_model", lambda f: FsmAgentStateModel(**f)
        )


class AgentDefinitionLoader:
    def __init__(self):
        self._json_loader = JSONFileLoader()

    def load(self, agent_def_path: str) -> AgentDefinition:
        loader_context = {}
        self._json_loader.load(
            context=loader_context,
            schema_path=AGENT_DEF_SCHEMA_PATH,
            file_path=agent_def_path,
            search_directories=search_directories(),
        )
        json_obj: dict = loader_context["json_content"]
        return AgentDefinition(**json_obj)
