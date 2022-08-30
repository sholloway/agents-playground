from argparse import Namespace
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, List, Union, ValuesView
from agents_playground.agents.structures import Size
from agents_playground.simulation.render_layer import RenderLayer

from agents_playground.simulation.tag import Tag
from agents_playground.agents.agent import Agent
from agents_playground.agents.path import InterpolatedPath

EntityGrouping = Dict[Tag, Namespace]

class NavigationMesh:
  def __init__(self) -> None:
    self.__junctions: Dict[Tag, SimpleNamespace] = dict()
    self.__segments: Dict[Tag, SimpleNamespace] = dict()

  def add_junction(self, junction) -> None:
    self.__junctions[junction.toml_id] = junction

  def add_segment(self, segment) -> None:
    self.__segments[segment.toml_id] = segment

  def junctions(self) -> ValuesView:
    return self.__junctions.values()
  
  def segments(self) -> ValuesView:
    return self.__segments.values()

  def get_junction(self, junction_toml_id: Tag) -> Namespace:
    if junction_toml_id in self.__junctions:
      return self.__junctions[junction_toml_id]
    else:
      raise Exception(f'NavigationMesh does not have a junction with ID = {junction_toml_id}.')
  
  def get_segment(self, segment_toml_id: Tag) -> Namespace:
    if segment_toml_id in self.__segments:
      return self.__segments[segment_toml_id]
    else:
      raise Exception(f'NavigationMesh does not have a segment with ID = {segment_toml_id}.')
    


@dataclass
class Scene:
  __cell_size: Size
  __cell_center_x_offset: float
  __cell_center_y_offset: float
  __entities: Dict[str, EntityGrouping]
  __layers: Dict[Tag, RenderLayer]
  __nav_mesh: NavigationMesh
  canvas_size: Size
  agents: Dict[Tag, Agent]
  paths: Dict[Tag, InterpolatedPath]

  def __init__(self) -> None:
    self.agents = dict()
    self.paths = dict()
    self.__entities = dict()
    self.__layers = dict()

  def add_agent(self, agent: Agent) -> None:
    self.agents[agent.id] = agent

  def add_path(self, path: InterpolatedPath) -> None:
    self.paths[path.id] = path

  @property
  def cell_size(self) -> Size: 
    return self.__cell_size

  @cell_size.setter
  def cell_size(self, size: Size) -> None:
    self.__cell_size = size
    self.__cell_center_x_offset = self.__cell_size.width/2.0
    self.__cell_center_y_offset = self.__cell_size.height/2.0

  @property
  def cell_center_x_offset(self) -> float:
    return self.__cell_center_x_offset
  
  @property
  def cell_center_y_offset(self) -> float:
    return self.__cell_center_y_offset

  @property
  def entities(self) -> Dict[str, EntityGrouping]:
    return self.__entities

  @property
  def nav_mesh(self) -> NavigationMesh:
    return self.__nav_mesh

  @nav_mesh.setter
  def nav_mesh(self, mesh: NavigationMesh) -> None:
    self.__nav_mesh = mesh

  def add_entity(self, grouping_name: str, entity: Namespace) -> None:
    if grouping_name not in self.__entities:
      self.__entities[grouping_name] = dict()
    entity.entity_grouping = grouping_name
    self.__entities[grouping_name][entity.toml_id] = entity

  def get_entity(self, grouping_name: str, entity_id: Any) -> Namespace:
    if grouping_name in self.__entities:
      if entity_id in self.__entities[grouping_name]:
        return self.__entities[grouping_name][entity_id]
      else:
        raise Exception(f'Scene.entities[{grouping_name}] does not have an entity with ID = {entity_id}.')
    else:
      raise Exception(f'Scene.entities does not have an entity grouping called: {grouping_name}.')
    
  def add_layer(self, layer: RenderLayer) -> None:
    self.__layers[layer.id] = layer

  def layers(self) -> ValuesView:
    """Returns an iterable view of the layer's dictionary."""
    return self.__layers.values()

  
