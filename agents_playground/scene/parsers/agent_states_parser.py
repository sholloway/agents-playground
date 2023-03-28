from types import SimpleNamespace
from typing import Dict

from agents_playground.agents.default.named_agent_state import NamedAgentActionState
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.scene.parsers.scene_parser import SceneParser
from agents_playground.scene.scene import Scene

class AgentStatesParser(SceneParser):
  def __init__(self, agent_state_definitions: Dict[str, AgentActionStateLike]) -> None:
    self._agent_state_definitions = agent_state_definitions

  def is_fit(self, scene_data: SimpleNamespace) -> bool:
    return hasattr(scene_data, 'agent_states')
  
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for agent_state in scene_data.agent_states:
      self._agent_state_definitions[agent_state.name] = NamedAgentActionState(agent_state.name)
    scene.agent_state_definitions = self._agent_state_definitions

  def default_process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    scene.agent_state_definitions = self._agent_state_definitions

  