from types import SimpleNamespace
from typing import Callable, Dict

from agents_playground.navigation.navigation_mesh import NavigationMesh
from agents_playground.legacy.scene.builders.nav_mesh_junction_builder import NavMeshJunctionBuilder
from agents_playground.legacy.scene.parsers.scene_parser import SceneParser
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.tag import Tag

class NavMeshJunctionParser(SceneParser):
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    render_map: Dict[str, Callable]
  ) -> None:
    self._id_generator = id_generator
    self._render_map   = render_map

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'nav_mesh')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    nav_mesh = NavigationMesh()

    if hasattr(scene_data.scene.nav_mesh, 'junctions'):
      for junction_def in scene_data.scene.nav_mesh.junctions:
        nav_mesh.add_junction(
          NavMeshJunctionBuilder.build(
            self._id_generator,
            self._render_map,
            junction_def
          )
        )

    scene.nav_mesh = nav_mesh