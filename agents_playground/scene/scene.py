from dataclasses import dataclass
from typing import Dict
from agents_playground.agents.structures import Size

from agents_playground.simulation.tag import Tag
from agents_playground.agents.agent import Agent
from agents_playground.agents.path import InterpolatedPath

@dataclass
class Scene:
  _cell_size: Size
  _cell_center_x_offset: float
  _cell_center_y_offset: float
  agents: Dict[Tag, Agent]
  paths: Dict[Tag, InterpolatedPath]

  def __init__(self) -> None:
    self.agents = dict()
    self.paths = dict()

  def add_agent(self, agent: Agent) -> None:
    self.agents[agent.id] = agent

  def add_path(self, path: InterpolatedPath) -> None:
    self.paths[path.id] = path

  @property
  def cell_size(self) -> None: 
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

    