from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, Iterator,  ValuesView, cast
from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike

from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.tick import Tick
from agents_playground.core.types import Size
from agents_playground.navigation.navigation_mesh import NavigationMesh
from agents_playground.scene.parsers.types import (
  AgentStateName, 
  AgentStateTransitionMapName, 
  DefaultAgentStateMap
)
from agents_playground.simulation.render_layer import RenderLayer
from agents_playground.simulation.tag import Tag
from agents_playground.paths.interpolated_path import InterpolatedPath

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

EntityGrouping = Dict[Tag, SimpleNamespace]

@dataclass
class Scene(Tick):
  _cell_size: Size
  _cell_center_x_offset: float
  _cell_center_y_offset: float
  _entities: Dict[str, EntityGrouping]
  _layers: Dict[Tag, RenderLayer]
  _nav_mesh: NavigationMesh
  canvas_size: Size
  agents: Dict[Tag, AgentLike]
  paths: Dict[Tag, InterpolatedPath]
  agent_state_definitions: Dict[AgentStateName, AgentActionStateLike]
  agent_transition_maps: Dict[AgentStateTransitionMapName, AgentActionSelector]
  default_agent_states: DefaultAgentStateMap

  def __init__(self) -> None:
    self.agents = dict()
    self.paths = dict()
    self._entities = dict()
    self._layers = dict()
    self._nav_mesh = NavigationMesh()

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

  def add_agent(self, agent: AgentLike) -> None:
    self.agents[agent.identity.id] = agent

  def add_path(self, path: InterpolatedPath) -> None:
    self.paths[path.id] = path

  def tick(self) -> None:
    """Called at the end of a frame."""
    agent: AgentLike
    for agent in self.agents.values():
      agent.tick()

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

  def visible_agents(self) -> Iterator[AgentLike]:
    return filter(lambda a: a.agent_state.visible, self.agents.values())