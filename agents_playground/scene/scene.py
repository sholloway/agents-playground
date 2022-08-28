from argparse import Namespace
from dataclasses import dataclass
from typing import Any, Dict, Union
from agents_playground.agents.structures import Size

from agents_playground.simulation.tag import Tag
from agents_playground.agents.agent import Agent
from agents_playground.agents.path import InterpolatedPath

EntityGrouping = Dict[Tag, Namespace]

@dataclass
class Scene:
  _cell_size: Size
  _cell_center_x_offset: float
  _cell_center_y_offset: float
  _entities: Dict[str, EntityGrouping]
  canvas_size: Size
  agents: Dict[Tag, Agent]
  paths: Dict[Tag, InterpolatedPath]

  def __init__(self) -> None:
    self.agents = dict()
    self.paths = dict()
    self._entities = dict()

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

  def add_entity(self, grouping_name: str, entity: Namespace) -> None:
    if grouping_name not in self._entities:
      self._entities[grouping_name] = dict()
    entity.entity_grouping = grouping_name
    self._entities[grouping_name][entity.toml_id] = entity

  def get_entity(self, grouping_name: str, entity_id: Any) -> Namespace:
    if grouping_name in self._entities:
      if entity_id in self._entities[grouping_name]:
        return self._entities[grouping_name][entity_id]
      else:
        raise Exception(f'Scene.entities[{grouping_name}] does not have an entity with ID = {entity_id}.')
    else:
      raise Exception(f'Scene.entities does not have an entity grouping called: {grouping_name}.')
    