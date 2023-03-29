from types import SimpleNamespace
from typing import Callable, Dict
from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector

from agents_playground.scene.builders.agent_builder import AgentBuilder
from agents_playground.scene.id_map import IdMap
from agents_playground.scene.parsers.scene_parser import SceneParser
from agents_playground.scene.parsers.types import AgentStateTransitionMapName
from agents_playground.scene.scene import Scene
from agents_playground.simulation.tag import Tag

class AgentsParser(SceneParser):
  """Create agents."""
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    id_map: IdMap,
    agent_transition_maps: Dict[AgentStateTransitionMapName, AgentActionSelector]
  ) -> None:
    self._id_generator = id_generator
    self._id_map       = id_map
    self._agent_transition_maps = agent_transition_maps

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'agents')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    # The first agent_state_transition_map defined is the default one to use.
    action_selector: AgentActionSelector = list(self._agent_transition_maps.values())[0]

    for agent_def in scene_data.scene.agents:
        if hasattr(agent_def, 'state_transition_map'):
          # Use the agent's preferred state map if one is defined.
          action_selector = self._agent_transition_maps[agent_def.state_transition_map]

        scene.add_agent(
        AgentBuilder.build(
          self._id_generator,
          self._id_map,
          agent_def,
          scene.cell_size,
          action_selector
        )
      )