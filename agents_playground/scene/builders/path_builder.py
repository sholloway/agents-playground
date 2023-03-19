from types import SimpleNamespace
from typing import Callable
from agents_playground.paths.circular_path import CirclePath
from agents_playground.paths.linear_path import LinearPath

from agents_playground.scene.id_map import IdMap
from agents_playground.simulation.tag import Tag


class PathBuilder:
  @staticmethod
  def build_linear_path(id_generator: Callable, render_map: dict, id_map: IdMap, linear_path_def: SimpleNamespace) -> LinearPath:
    path_id: Tag = id_generator()
    id_map.register_linear_path(path_id, linear_path_def.id)
    lp = LinearPath(
      id = path_id, 
      control_points = tuple(linear_path_def.steps), 
      renderer = render_map[linear_path_def.renderer],
      toml_id = linear_path_def.id
    )

    if hasattr(linear_path_def, 'closed'):
      lp.closed = linear_path_def.closed

    return lp

  @staticmethod
  def build_circular_path(id_generator: Callable, render_map: dict, id_map: IdMap, circular_path_def: SimpleNamespace) -> CirclePath:
    path_id: Tag = id_generator()
    id_map.register_circular_path(path_id, circular_path_def.id)
    cp = CirclePath(
      id =path_id,
      center = (float(circular_path_def.center[0]), float(circular_path_def.center[1])),
      radius = circular_path_def.radius,
      renderer = render_map[circular_path_def.renderer],
      toml_id = circular_path_def.id
    )
    return cp