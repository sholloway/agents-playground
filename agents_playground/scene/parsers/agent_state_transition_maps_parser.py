from types import SimpleNamespace
from typing import Callable, Dict, List
from agents_playground.agents.default.default_agent_action_state_rules_set import DefaultAgentActionStateRulesSet

from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_action_state_rules_set import AgentActionStateRulesSet
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_state_transition_rule import AgentStateTransitionRule
from agents_playground.likelihood.coin import Coin
from agents_playground.likelihood.weighted_coin import WeightedCoin
from agents_playground.scene.parsers.invalid_scene_exception import InvalidSceneException
from agents_playground.scene.parsers.scene_parser import SceneParser
from agents_playground.scene.parsers.types import DefaultAgentStatesDict, TransitionCondition
from agents_playground.scene.scene import Scene

class AgentStateTransitionMapsParser(SceneParser):
  def __init__(
    self, 
    agent_state_definitions: Dict[str, AgentActionStateLike], 
    agent_transition_maps: Dict[str, AgentActionSelector],
    default_agent_states: DefaultAgentStatesDict,
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
    # 1. Is the state name a registered state?
    # 2. Build up ?
    """
    transition_rule: SimpleNamespace
    for transition_map_name, transition_map in vars(scene_data.agent_state_transition_maps).items():
      rules_list: List[AgentStateTransitionRule] = []
      for transition_rule in transition_map:  
        if transition_rule.state in self._agent_state_definitions:
          state: AgentActionStateLike = self._agent_state_definitions[transition_rule.state]
          next_state: AgentActionStateLike = self._agent_state_definitions[transition_rule.transitions_to]
          transition_condition: TransitionCondition = self._parse_rule_condition(transition_rule)
          likelihood: Coin = self._parse_likelihood(transition_rule)
          rules_list.append(
            AgentStateTransitionRule(
              state         = state,
              transition_to = next_state,
              condition     = transition_condition,
              likelihood    = likelihood
            )
          )
        else:
          msg = (
            'Invalid scene.toml file.'
            'You must declare states in scene.agent_states before using them in agent_state_transition_maps.'
            f'The agent_state_transition_maps {transition_map_name} used state = {transition_rule.state}.'
            f'However, {transition_rule.state} is not defined in scene.agent_states.'
          ) 
          raise InvalidSceneException(msg)
      rule_set: AgentActionStateRulesSet = DefaultAgentActionStateRulesSet(
        rules = rules_list,
        default_state = self._default_agent_states[transition_map_name]
      )
  
  def _parse_rule_condition(self, transition_rule: SimpleNamespace) -> TransitionCondition:
    condition: TransitionCondition
    if hasattr(transition_rule, 'when'):
      if transition_rule.when in self._state_transition_conditions_map:
        condition = self.self._conditions_map[transition_rule.when]  
      else:
        msg = (
          'Invalid scene.toml file.'
          'The "when" field on an agent_state_transition_maps rule must be registered in AGENT_ACTION_STATE_TRANSITION_REGISTRY or the SimulationExtensions.'
          'Could not find condition function {transition_rule.when}'
        )
        raise InvalidSceneException(msg)
    else:
      condition = self.self._conditions_map['always_transition']
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

"""
There's a lot of moving pieces. I'm getting confused on what does what.

The Agent Instance Hierarchy
agent: AgentLike
    agent_state: AgentStateLike
      action_selector: AgentActionSelector

Ultimately I want to dynamically build the AgentActionSelector for each 
agent based on what's declared in the scene.toml file.

action_selector: FuzzyAgentActionSelector
  self._state_map: dict[AgentActionStateLike, AgentActionStateRulesSet]

AgentActionStateRulesSet
  rules: List[AgentStateTransitionRule]

How to deal with setting the default state?
Option 1: Set it in scene.agent_states
agent_states = [
  { name = 'IDLE_STATE', default=True},
  { name = 'RESTING_STATE'},
  { name = 'PLANNING_STATE'},
  { name = 'ROUTING_STATE'},
  { name = 'TRAVELING_STATE'}
]

This is easy however the limitation is that all state maps defined in the TOML 
must use the same default unless it's overridden programmatically.

Option 2. Map default states to transition maps.
[scene]
default_agent_states = [
  { agent_state_transition_map = '', default_state=''}
] 

This approach is verbose, requires additional memory, and must be parsed before 
agent_state_transition_maps, but it provides flexibility.

Option 3. Support option 2 and if there is no scene.default_agent_states then 
use the first agent_states item declared as the default.

"""