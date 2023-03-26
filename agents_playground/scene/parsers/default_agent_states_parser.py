from types import SimpleNamespace
from typing import Dict
from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.scene.parsers.scene_parser import SceneParser
from agents_playground.scene.parsers.types import AgentStateName, DefaultAgentStatesDict
from agents_playground.scene.scene import Scene

class DefaultAgentStates(dict):
  default_value: AgentActionStateLike
  
  def __init__(self, **kwargs) -> None:
    super(DefaultAgentStates, self).__init__(**kwargs)

  def __getitem__(self, key):
    if key in self:
      return super(DefaultAgentStates, self).__getitem__(key)
    elif self.default_value:
      return self.default_value
    else:
      raise KeyError(f'The key {key} was not found and the default value was not')

class DefaultAgentStatesParser(SceneParser):
  def __init__(
    self, 
    default_agent_states: DefaultAgentStatesDict, 
    agent_state_definitions: Dict[AgentStateName, AgentActionStateLike]
  ) -> None:
    super().__init__()
    self._default_agent_states = default_agent_states
    self._agent_state_definitions = agent_state_definitions

  def is_fit(self, scene_data: SimpleNamespace) -> bool:
    return hasattr(scene_data, 'default_agent_states')
  
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    self.default_process(scene_data, scene)

    default_mapping: SimpleNamespace
    for default_mapping in scene_data.default_agent_states:
      self._default_agent_states[default_mapping.agent_state_transition_map] = default_mapping.default_state

  def default_process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    self._default_agent_states.default_value = list(self._agent_state_definitions.values())[0]