from types import SimpleNamespace
from typing import Callable, Dict

from agents_playground.legacy.scene.builders.layer_builder import LayerBuilder
from agents_playground.legacy.scene.parsers.scene_parser import SceneParser
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.tag import Tag

class SceneLayersParser(SceneParser):
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    render_map: Dict[str, Callable]
  ) -> None:
    self._id_generator = id_generator
    self._render_map   = render_map

  """Create render-able Layers"""
  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'layers')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for layer_def in scene_data.scene.layers:
      scene.add_layer(LayerBuilder.build(self._id_generator, self._render_map, layer_def))