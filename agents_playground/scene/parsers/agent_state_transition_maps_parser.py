from types import SimpleNamespace
from typing import Callable, Dict, List, Tuple, cast
from agents_playground.agents.default.default_agent_action_state_rules_set import DefaultAgentActionStateRulesSet
from agents_playground.agents.default.fuzzy_agent_action_selector import FuzzyAgentActionSelector
from agents_playground.agents.default.map_agent_action_selector import MapAgentActionSelector

from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_action_state_rules_set import AgentActionStateRulesSet
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_state_transition_rule import AgentStateTransitionRule
from agents_playground.likelihood.coin import Coin
from agents_playground.likelihood.weighted_coin import WeightedCoin
from agents_playground.scene.parsers.invalid_scene_exception import InvalidSceneException
from agents_playground.scene.parsers.parser_utilities import require_attr
from agents_playground.scene.parsers.scene_parser import SceneParser
from agents_playground.scene.parsers.types import AgentStateTransitionMapName, DefaultAgentStateMap, TransitionCondition
from agents_playground.scene.scene import Scene

class AgentStateTransitionMapsParser(SceneParser):
  def __init__(
    self, 
    agent_state_definitions: Dict[str, AgentActionStateLike], 
    agent_transition_maps: Dict[str, AgentActionSelector],
    default_agent_states: DefaultAgentStateMap,
    likelihood_map: Dict[str, Coin],
    conditions_map: Dict[str, Callable[[AgentCharacteristics],bool]]
  ) -> None:
    self._agent_state_definitions = agent_state_definitions
    self._agent_transition_maps = agent_transition_maps
    self._default_agent_states = default_agent_states
    self._likelihood_map = likelihood_map
    self._conditions_map = conditions_map

  def is_fit(self, scene_data: SimpleNamespace) -> bool:
    return hasattr(scene_data, 'agent_state_transition_maps')
  
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    """
    Parse scene.agent_state_transition_maps in the scene.toml file and store it 
    in Scene.agent_transition_maps.
    """
    transition_map_name: str
    transition_map: List[SimpleNamespace]
    for transition_map_name, transition_map in vars(scene_data.agent_state_transition_maps).items():
      # Produce a flat rule set.
      rule_set: AgentActionStateRulesSet = self._parse_state_transition_map(transition_map_name, transition_map)

      # Group the rule sets by their state attribute.
      state_map = self._build_state_specific_rule_sets(rule_set)

      self._agent_transition_maps[transition_map_name] = FuzzyAgentActionSelector(state_map)
    scene.agent_transition_maps = self._agent_transition_maps

  def default_process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    """
    Since agent_state_transition_maps was not defined in the scene.toml file 
    create an empty transition map for agent assignment. 
    """
    self._agent_transition_maps['default_agent_state_map'] = MapAgentActionSelector(state_map = {})
    scene.agent_transition_maps = self._agent_transition_maps
  
  def _parse_state_transition_map(
    self, 
    transition_map_name: str, 
    transition_map: List[SimpleNamespace]
  ) -> AgentActionStateRulesSet:
    rules_list: List[AgentStateTransitionRule] = []
    transition_rule: SimpleNamespace
    for transition_rule in transition_map:  
      require_attr(transition_rule, 'state', 'State attribute must be defined on state transition rules.')
      require_attr(transition_rule, 'transitions_to', 'The attribute transitions_to must be defined on state transition rules.')

      if transition_rule.state in self._agent_state_definitions:
        state: AgentActionStateLike = self._agent_state_definitions[transition_rule.state]
        next_state: AgentActionStateLike | Tuple[AgentActionStateLike, ...]  = self._parse_transitions_to(transition_rule, self._agent_state_definitions)
        choice_weights: Tuple[float, ...] = self._parse_transition_chances(transition_rule)
        transition_condition: TransitionCondition = self._parse_rule_condition(transition_rule)
        likelihood: Coin = self._parse_likelihood(transition_rule)
        rules_list.append(
          AgentStateTransitionRule(
            state          = state,
            transition_to  = next_state,
            condition      = transition_condition,
            likelihood     = likelihood,
            choice_weights = choice_weights
          )
        )
      else:
        msg = (
          'Invalid scene.toml file.\n'
          'You must declare states in scene.agent_states before using them in agent_state_transition_maps.\n'
          f'The agent_state_transition_maps {transition_map_name} referenced state = {transition_rule.state}.\n'
          f'However, {transition_rule.state} is not defined in scene.agent_states.\n'
          f'{list(self._agent_state_definitions.keys())}'
        ) 
        raise InvalidSceneException(msg)
    rule_set: AgentActionStateRulesSet = DefaultAgentActionStateRulesSet(
      rules = rules_list,
      default_state = self._default_agent_states[transition_map_name]
    )
    return rule_set
  
  def _parse_transitions_to(
    self, 
    transition_rule: SimpleNamespace, 
    agent_state_definitions: Dict[str, AgentActionStateLike]
  ) -> AgentActionStateLike | Tuple[AgentActionStateLike, ...]:
    """
    A state transition map can have an explicit next state or a list of choices.
    Parse the values and return either the mapped AgentActionStateLike or a tuple
    of the choices.
    """
    if isinstance(transition_rule.transitions_to, tuple):
      possible_future_states: List[AgentActionStateLike] = []
      for possible_state in transition_rule.transitions_to:
        possible_future_states.append(agent_state_definitions[possible_state])
      if len(possible_future_states) > 0:
        return tuple(possible_future_states)
      else:
        msg = (
          'Error processing scene.toml file.'
          'Was unable to construct a state transition rule.'
          'Make sure that all states are defined before using them in transition rules.'
        )
        raise InvalidSceneException(msg)
    elif isinstance(transition_rule.transitions_to, str):
      return agent_state_definitions[transition_rule.transitions_to]
    else:
      msg = (
        'Invalid scene.toml file.'
        'The attribute transition_rule must be a tuple or string.'
        f'Instead it was an instance of a {type(transition_rule.transitions_to)}'
        )
      raise InvalidSceneException(msg)
  
  def _parse_transition_chances(self, transition_rule: SimpleNamespace) -> Tuple[float, ...]:
    """Find the declared chances on a state transition rule or build one."""
    if hasattr(transition_rule, 'chances'):
      return cast(Tuple[float, ...], transition_rule.transition_rule)
    else:
      return tuple() # All choices have an equal probability so just return an empty tuple.

  def _build_state_specific_rule_sets(self, rule_set: AgentActionStateRulesSet) -> dict[AgentActionStateLike, AgentActionStateRulesSet]:
    state_map: dict[AgentActionStateLike, AgentActionStateRulesSet] = {}

    default_state: AgentActionStateLike
    if isinstance(rule_set.no_rule_resolved.transition_to, tuple):
      default_state = rule_set.no_rule_resolved.transition_to[0]
    else:
      default_state = rule_set.no_rule_resolved.transition_to
    
    # Find each unique state name in the rule_set. We need the AgentActionStateLike for that name.
    agent_states_with_rules: List[AgentActionStateLike] = list(set(map(lambda rule: rule.state, rule_set.rules)))

    # For each unique state, use filter to get all the rules for that.
    # Then, Create a new AgentActionStateRulesSet that has just those rules and default state.
    for agent_state in agent_states_with_rules:
      state_specific_rules: List[AgentStateTransitionRule] = list(filter(lambda rule: rule.state == agent_state,  rule_set.rules))
      state_map[agent_state] = DefaultAgentActionStateRulesSet(state_specific_rules, default_state)

    return state_map

  def _parse_rule_condition(self, transition_rule: SimpleNamespace) -> TransitionCondition:
    condition: TransitionCondition
    if hasattr(transition_rule, 'when'):
      if transition_rule.when in self._conditions_map:
        condition = self._conditions_map[transition_rule.when]  
      else:
        msg = (
          'Invalid scene.toml file.'
          'The "when" field on an agent_state_transition_maps rule must be registered in AGENT_ACTION_STATE_TRANSITION_REGISTRY or the SimulationExtensions.'
          'Could not find condition function {transition_rule.when}'
        )
        raise InvalidSceneException(msg)
    else:
      condition = self._conditions_map['always_transition']
    return condition

  def _parse_likelihood(self, transition_rule: SimpleNamespace) -> Coin:
    likelihood: Coin
    if hasattr(transition_rule, 'likelihood'):
      likelihood = WeightedCoin(weight = float(transition_rule.likelihood))
    elif hasattr(transition_rule, 'coin'): 
      likelihood = self._likelihood_map[transition_rule.coin]
    else:
      likelihood = self._likelihood_map['always_heads']
    return likelihood
