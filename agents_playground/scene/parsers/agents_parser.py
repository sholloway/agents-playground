from types import SimpleNamespace
from typing import Callable

from agents_playground.scene.builders.agent_builder import AgentBuilder
from agents_playground.scene.id_map import IdMap
from agents_playground.scene.parsers.scene_parser import SceneParser
from agents_playground.scene.scene import Scene
from agents_playground.simulation.tag import Tag

class AgentsParser(SceneParser):
  """Create agents."""
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    id_map: IdMap
  ) -> None:
    self._id_generator = id_generator
    self._id_map       = id_map

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'agents')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for agent_def in scene_data.scene.agents:
        scene.add_agent(
        AgentBuilder.build(
          self._id_generator,
          self._id_map,
          agent_def,
          scene.cell_size
        )
      )