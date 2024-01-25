from types import SimpleNamespace
from typing import Dict
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.legacy.scene.parsers.scene_parser import SceneParser
from agents_playground.legacy.scene.parsers.types import AgentStateName, AgentStateTransitionMapName, DefaultAgentStateMap
from agents_playground.legacy.scene.scene import Scene

class DefaultAgentStatesParser(SceneParser):
  """
  Parses the optional scene.default_agent_states section. 
  
  Map default states to transition maps.
  if there is no scene.default_agent_states then the engine will use the 
  first agent_states item declared as the default state for each agent_state_transition_map.

  TOML Example:
  default_agent_states = [
    { agent_state_transition_map = 'default_agent_state_map', default_state='IDLE_STATE' }
  ]
  """
  def __init__(
    self, 
    default_agent_states: DefaultAgentStateMap, 
    agent_state_definitions: Dict[AgentStateName, AgentActionStateLike]
  ) -> None:
    super().__init__()
    self._default_agent_states = default_agent_states
    self._agent_state_definitions = agent_state_definitions

  
  def parse(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    if self.is_fit(scene_data):
      self.default_process(scene_data, scene)
      self.process(scene_data, scene)
    else:
      self.default_process(scene_data, scene)
    scene.default_agent_states = self._default_agent_states

  def is_fit(self, scene_data: SimpleNamespace) -> bool:
    return hasattr(scene_data, 'default_agent_states')
  
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    default_mapping: SimpleNamespace
    for default_mapping in scene_data.default_agent_states:
      self._default_agent_states[default_mapping.agent_state_transition_map] = default_mapping.default_state
  

  def default_process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    if len(self._agent_state_definitions) > 0:
      self._default_agent_states.default_value = list(self._agent_state_definitions.values())[0]