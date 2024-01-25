from agents_playground.legacy.scene.id_map import IdMap
from agents_playground.legacy.scene.parsers.circular_path_parser import CircularPathParser
from agents_playground.legacy.scene.parsers.linear_path_parser import LinearPathParser
from agents_playground.legacy.scene.parsers.scene_parser import SceneParser
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.tag import Tag


from types import SimpleNamespace
from typing import Callable, Dict, List


class PathsParser(SceneParser):
  """Create paths."""
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    id_map: IdMap,
    render_map: Dict[str, Callable]
  ) -> None:
    self._parsers: List[SceneParser] =  [
      LinearPathParser(id_generator, id_map, render_map),
      CircularPathParser(id_generator, id_map, render_map)
    ]

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'paths')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for parser in self._parsers:
      parser.parse(scene_data, scene)