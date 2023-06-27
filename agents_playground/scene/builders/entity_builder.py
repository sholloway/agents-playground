from __future__ import annotations

from copy import deepcopy
from types import MethodType, SimpleNamespace
from typing import Callable, Dict

from agents_playground.renderers.color import Color
from agents_playground.scene.id_map import IdMap
from agents_playground.scene.parsers.scene_parser_exception import SceneParserException
from agents_playground.simulation.tag import Tag
from agents_playground.spatial.types import Coordinate

class EntityBuilder:
  @staticmethod
  def build(id_generator: Callable, 
    renderer_map: dict, 
    entity_def: SimpleNamespace, 
    entities_map: Dict[str, Callable], 
    id_map: IdMap) -> SimpleNamespace:
    """
    Builds an entity object by cloning the definition from the TOML file and 
    assigning attributes needed for rendering.
    """
    entity = deepcopy(entity_def)
    entity.toml_id = entity.id
    entity.id = id_generator()
    
    _parse_entity_renderer(entity_def, renderer_map, entity)
    _parse_update_method(entity_def, entities_map, entity)
    _parse_location(entity_def, entity)
    _parse_color(entity_def, entity)
    _parse_fill(entity_def, entity)
    _parse_related(entity_def, entity, id_map)

    return entity
  
def _parse_entity_renderer(entity_def: SimpleNamespace, renderer_map: dict, entity: SimpleNamespace):
  if hasattr(entity_def,'renderer'):
    if not entity_def.renderer in renderer_map:
      err_msg = (
        f'Invalid scene.toml file.\n'
        f'An entity definition references renderer {entity_def.renderer} but it is not registered.\n'
        f'Use the agents_playground.project.extensions.register_renderer decorator to register a rendering function.'
      )
      raise SceneParserException(err_msg)
    entity.render = MethodType(renderer_map[entity_def.renderer], entity)
  else:
    entity.render = MethodType(renderer_map['do_nothing_render'], entity)
  
def _parse_update_method(entity_def: SimpleNamespace, entities_map: Dict[str, Callable], entity: SimpleNamespace):
  if hasattr(entity_def, 'update_method'):
    if not entity_def.update_method in entities_map:
      err_msg = (
        f'Invalid scene.toml file.\n'
        f'An entity definition references update_method {entity_def.update_method} but it is not registered.\n'
        f'Use the agents_playground.project.extensions.register_entity decorator to register an entity update function.'
      )
      raise SceneParserException(err_msg)
    entity.update = MethodType(entities_map[entity_def.update_method], entity)
  else:
    entity.update = MethodType(entities_map['do_nothing_update_method'], entity)

def _parse_location(entity_def: SimpleNamespace, entity: SimpleNamespace):
  if hasattr(entity_def, 'location'):
    entity.location = Coordinate(*entity_def.location)

def _parse_color(entity_def: SimpleNamespace, entity: SimpleNamespace):
  if hasattr(entity_def, 'color'):
    entity.color = Color(*entity_def.color)

def _parse_fill(entity_def: SimpleNamespace, entity: SimpleNamespace):
  if hasattr(entity_def, 'fill'):
    entity.fill = Color(*entity_def.fill)

def _parse_related(entity_def: SimpleNamespace, entity: SimpleNamespace, id_map: IdMap):
  if hasattr(entity_def, 'related') and hasattr(entity_def, 'related_id'):
    if entity_def.related == 'agent':
      agent_toml_id: Tag = entity_def.related_id
      try:
        agent_id: Tag = id_map.lookup_agent_by_toml(agent_toml_id)
        entity.agent_id = agent_id
      except KeyError:
        err_msg = (
          f'Invalid scene.toml file.\n'
          f'An entity definition references an agent by it\'s TOML id {agent_toml_id}.\n'
          f'There is no agent registered with that ID.'
        )
        raise SceneParserException(err_msg)
    else:
      err_msg = (
        f'Invalid scene.toml file.\n'
        f'An entity definition contains related={entity_def.related}.'
        f'This is currently not supported.'
      )
      raise SceneParserException(err_msg)