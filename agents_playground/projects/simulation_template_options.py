from typing import NamedTuple

class SimulationTemplateOptions(NamedTuple):
  simulation_name: str
  simulation_title: str
  simulation_description: str
  parent_directory: str
  creation_time: str
  scene_uom_system: str
  scene_distance_uom: str 
  landscape_uom_system: str
  tile_size_uom: str 
  author: str
  license: str
  contact: str 