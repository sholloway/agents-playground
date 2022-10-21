from argparse import Namespace
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, Iterator, Union, ValuesView, cast
from agents_playground.core.types import Size

from agents_playground.navigation.navigation_mesh import NavigationMesh
from agents_playground.simulation.render_layer import RenderLayer
from agents_playground.simulation.tag import Tag
from agents_playground.agents.agent import Agent
from agents_playground.paths.interpolated_path import InterpolatedPath
from agents_playground.styles.agent_style import AgentStyle
from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

EntityGrouping = Dict[Tag, SimpleNamespace]

@dataclass
class Scene:
  _cell_size: Size
  _cell_center_x_offset: float
  _cell_center_y_offset: float
  _entities: Dict[str, EntityGrouping]
  _layers: Dict[Tag, RenderLayer]
  _nav_mesh: NavigationMesh
  canvas_size: Size
  agents: Dict[Tag, Agent]
  paths: Dict[Tag, InterpolatedPath]
  agent_style: AgentStyle

  def __init__(self) -> None:
    self.agents = dict()
    self.paths = dict()
    self._entities = dict()
    self._layers = dict()
    self._nav_mesh = NavigationMesh()
    self.agent_style = AgentStyle()

  def __del__(self) -> None:
    logger.info('Scene is deleted.')

  def purge(self) -> None:
    self._cell_size = cast(Size, None)
    self._cell_center_x_offset = cast(float, None)
    self._cell_center_y_offset = cast(float, None)
    self.canvas_size = cast(Size, None)
    self._entities.clear()
    self._layers.clear()
    self._nav_mesh.purge()
    self.agents.clear()
    self.paths.clear()

  def add_agent(self, agent: Agent) -> None:
    self.agents[agent.id] = agent

  def add_path(self, path: InterpolatedPath) -> None:
    self.paths[path.id] = path

  @property
  def cell_size(self) -> Size: 
    return self._cell_size

  @cell_size.setter
  def cell_size(self, size: Size) -> None:
    self._cell_size = size
    self._cell_center_x_offset = self._cell_size.width/2.0
    self._cell_center_y_offset = self._cell_size.height/2.0

  @property
  def cell_center_x_offset(self) -> float:
    return self._cell_center_x_offset
  
  @property
  def cell_center_y_offset(self) -> float:
    return self._cell_center_y_offset

  @property
  def entities(self) -> Dict[str, EntityGrouping]:
    return self._entities

  @property
  def nav_mesh(self) -> NavigationMesh:
    return self._nav_mesh

  @nav_mesh.setter
  def nav_mesh(self, mesh: NavigationMesh) -> None:
    self._nav_mesh = mesh

  def add_entity(self, grouping_name: str, entity: SimpleNamespace) -> None:
    if grouping_name not in self._entities:
      self._entities[grouping_name] = dict()
    entity.entity_grouping = grouping_name
    self._entities[grouping_name][entity.toml_id] = entity

  def get_entity(self, grouping_name: str, entity_id: Any) -> SimpleNamespace:
    if grouping_name in self._entities:
      if entity_id in self._entities[grouping_name]:
        return self._entities[grouping_name][entity_id]
      else:
        raise Exception(f'Scene.entities[{grouping_name}] does not have an entity with ID = {entity_id}.')
    else:
      raise Exception(f'Scene.entities does not have an entity grouping called: {grouping_name}.')
    
  def add_layer(self, layer: RenderLayer) -> None:
    self._layers[layer.id] = layer

  def layers(self) -> ValuesView:
    """Returns an iterable view of the layer's dictionary."""
    return self._layers.values()

  def visible_agents(self) -> Iterator[Agent]:
    return filter(lambda a: a.visible, self.agents.values())
