from types import SimpleNamespace
from typing import Callable, Dict

from agents_playground.legacy.scene.builders.entity_builder import EntityBuilder
from agents_playground.legacy.scene.id_map import IdMap
from agents_playground.legacy.scene.parsers.scene_parser import SceneParser
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.tag import Tag

class EntitiesParser(SceneParser):
  """
  Creates entities. 
  The format for an entity is that each item is an instance of a Namespace. 
  For example:
    [[scene.entities.circles]]
    [[scene.entities.structures.buildings]]
    [[scene.entities.structures.portals]]
  """
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    render_map: Dict[str, Callable],
    entities_map: Dict[str, Callable],
    id_map: IdMap
  ) -> None:
    self._id_generator = id_generator
    self._render_map   = render_map
    self._entities_map = entities_map
    self._id_map       = id_map

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'entities')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for grouping_name, entity_grouping in vars(scene_data.scene.entities).items():
      for entity in entity_grouping:
        scene.add_entity(
          grouping_name,
          EntityBuilder.build(
            self._id_generator,
            self._render_map,
            entity,
            self._entities_map,
            self._id_map 
          )
        )