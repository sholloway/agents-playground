from types import SimpleNamespace
from typing import Callable, Dict

from agents_playground.legacy.scene.builders.path_builder import PathBuilder
from agents_playground.legacy.scene.id_map import IdMap
from agents_playground.legacy.scene.parsers.scene_parser import SceneParser
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.tag import Tag

class CircularPathParser(SceneParser):
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    id_map: IdMap,
    render_map: Dict[str, Callable]
  ) -> None:
    self._id_generator = id_generator
    self._id_map       = id_map
    self._render_map   = render_map

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene.paths, 'circular')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for circular_path_def in scene_data.scene.paths.circular:
      scene.add_path(PathBuilder.build_circular_path(self._id_generator, self._render_map, self._id_map, circular_path_def))