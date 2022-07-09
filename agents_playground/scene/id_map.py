
from typing import Dict
from agents_playground.simulation.tag import Tag

class IdMap:
  def __init__(self) -> None:
    self._agents_toml_to_dpg: Dict[Tag, Tag] = {}
    self._agents_dpg_to_toml: Dict[Tag, Tag] = {}
    self._linear_paths_toml_to_dpg: Dict[Tag, Tag] = {}
    self._linear_paths_dpg_to_toml: Dict[Tag, Tag] = {}
    self._circular_paths_toml_to_dpg: Dict[Tag, Tag] = {}
    self._circular_paths_dpg_to_toml: Dict[Tag, Tag] = {}

  def register_agent(self, agent_id: Tag, toml_id: Tag) -> None:
    self._agents_toml_to_dpg[toml_id] = agent_id
    self._agents_dpg_to_toml[agent_id] = toml_id

  def register_linear_path(self, path_id: Tag, toml_id: Tag) -> None:
    self._linear_paths_toml_to_dpg[toml_id] = path_id
    self._linear_paths_dpg_to_toml[path_id] = toml_id

  def register_circular_path(self, path_id: Tag, toml_id: Tag) -> None:
    self._circular_paths_toml_to_dpg[toml_id] = path_id
    self._circular_paths_dpg_to_toml[path_id] = toml_id

  def lookup_agent_by_toml(self, toml_id: Tag) -> Tag:
    return self._agents_toml_to_dpg[toml_id]

  def lookup_agent_by_dpg(self, agent_id: Tag) -> Tag:
    return self._agents_dpg_to_toml[agent_id]
  
  def lookup_linear_path_by_toml(self, toml_id: Tag) -> Tag:
    return self._linear_paths_toml_to_dpg[toml_id]

  def lookup_linear_path_by_dpg(self, path_id: Tag) -> Tag:
    return self._linear_paths_dpg_to_toml[path_id]
  
  def lookup_circular_path_by_toml(self, toml_id: Tag) -> Tag:
    return self._circular_paths_toml_to_dpg[toml_id]

  def lookup_circular_path_by_dpg(self, path_id: Tag) -> Tag:
    return self._circular_paths_dpg_to_toml[path_id]