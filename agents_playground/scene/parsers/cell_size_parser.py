from types import SimpleNamespace

from agents_playground.core.types import Size
from agents_playground.scene.parsers.scene_parser import SceneParser
from agents_playground.scene.scene import Scene
from agents_playground.scene.scene_defaults import SceneDefaults

class CellSizeParser(SceneParser):
  """Establish the cell size on the 2D grid."""
  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'cell_size')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    scene.cell_size = Size(*scene_data.scene.cell_size)

  def default_action(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    scene.cell_size = SceneDefaults.CELL_SIZE