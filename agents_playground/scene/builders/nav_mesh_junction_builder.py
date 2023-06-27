from copy import deepcopy
from types import MethodType, SimpleNamespace
from typing import Callable

from agents_playground.spatial.types import Coordinate

class NavMeshJunctionBuilder:
  @staticmethod
  def build(
    id_generator: Callable, 
    renderer_map: dict, 
    junction_def: SimpleNamespace
  ) -> SimpleNamespace:
    junction = deepcopy(junction_def)
    junction.toml_id = junction_def.id
    junction.id = id_generator()

    if hasattr(junction_def, 'location'):
      junction.location = Coordinate(*junction_def.location)
      
    if hasattr(junction_def,'renderer'):
      junction.render = MethodType(renderer_map[junction_def.renderer], junction)
    else:
      junction_def.render = MethodType(renderer_map['do_nothing_render'], junction_def)

    return junction