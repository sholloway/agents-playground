from types import SimpleNamespace

from agents_playground.core.types import Size
from agents_playground.legacy.scene.parsers.scene_parser import SceneParser
from agents_playground.legacy.scene.scene import Scene

class CanvasSizeParser(SceneParser):
  """Set the canvas size if present."""
  def parse(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    canvas_width = scene_data.scene.width if hasattr(scene_data.scene, 'width') else None
    canvas_height = scene_data.scene.height if hasattr(scene_data.scene, 'height') else None
    scene.canvas_size = Size(canvas_width, canvas_height)

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return True

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    pass