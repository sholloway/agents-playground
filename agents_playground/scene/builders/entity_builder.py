from copy import deepcopy
from types import MethodType, SimpleNamespace
from typing import Callable, Dict

from agents_playground.core.types import Coordinate
from agents_playground.renderers.color import Color


class EntityBuilder:
  @staticmethod
  def build(id_generator: Callable, 
    renderer_map: dict, 
    entity_def: SimpleNamespace, 
    entities_map: Dict[str, Callable]) -> SimpleNamespace:
    """
    Builds an entity object by cloning the definition from the TOML file and 
    assigning attributes needed for rendering.
    """
    entity = deepcopy(entity_def)
    entity.toml_id = entity.id
    entity.id = id_generator()
    if hasattr(entity_def,'renderer'):
      entity.render = MethodType(renderer_map[entity_def.renderer], entity)
    else:
      entity.render = MethodType(renderer_map['do_nothing_render'], entity)

    if hasattr(entity_def, 'update_method'):
      entity.update = MethodType(entities_map[entity_def.update_method], entity)
    else:
      entity.update = MethodType(entities_map['do_nothing_update_method'], entity)

    if hasattr(entity_def, 'location'):
      entity.location = Coordinate(*entity_def.location)

    if hasattr(entity_def, 'color'):
      entity.color = Color(*entity_def.color)
    
    if hasattr(entity_def, 'fill'):
      entity.fill = Color(*entity_def.fill)
      
    return entity