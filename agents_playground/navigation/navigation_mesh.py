from argparse import Namespace
from types import SimpleNamespace
from typing import Dict, List, ValuesView

from agents_playground.agents.structures import Point
from agents_playground.simulation.tag import Tag

Junction = SimpleNamespace

class NavigationMesh:
  def __init__(self) -> None:
    self.__junctions: Dict[Tag, Junction] = dict()
    self.__junction_location_index: Dict[Point, Tag] = dict()

  def add_junction(self, junction: Junction) -> None:
    if junction.toml_id in self.__junctions:
      raise Exception(f'The junction {junction.toml_id} is already defined in the navigation mesh.')
    else:
      self.__junctions[junction.toml_id] = junction
      self.__junction_location_index[junction.location] = junction.toml_id

  def junctions(self) -> ValuesView:
    return self.__junctions.values()

  def get_junction_by_toml_id(self, junction_toml_id: Tag) -> Junction:
    if junction_toml_id in self.__junctions:
      return self.__junctions[junction_toml_id]
    else:
      raise Exception(f'NavigationMesh does not have a junction with TOML ID = {junction_toml_id}.')
  
  def get_junction_by_location(self, location: Point) -> Junction:
    if location in self.__junction_location_index:
      toml_id = self.__junction_location_index[location]
      return self.get_junction_by_toml_id(toml_id)
    else:
      raise Exception(f'NavigationMesh does not have a junction at location {location}.')