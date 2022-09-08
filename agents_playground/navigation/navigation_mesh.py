from argparse import Namespace
from types import SimpleNamespace
from typing import Dict, List, ValuesView
from agents_playground.agents.structures import Point

from agents_playground.simulation.tag import Tag

Junction = SimpleNamespace
Segment = SimpleNamespace
class NavigationMesh:
  def __init__(self) -> None:
    self.__junctions: Dict[Tag, SimpleNamespace] = dict()
    self.__junction_location_index: Dict[Point, Tag] = dict()
    self.__segments: Dict[Tag, SimpleNamespace] = dict()
    self.__segments_junction_index: Dict[str, Tag] = dict()

  def add_junction(self, junction: SimpleNamespace) -> None:
    self.__junctions[junction.toml_id] = junction
    self.__junction_location_index[junction.location] = junction.toml_id

  def add_segment(self, segment: SimpleNamespace) -> None:
    self.__segments[segment.toml_id] = segment
    self.__segments_junction_index[segment.junction] = segment.toml_id

  def junctions(self) -> ValuesView:
    return self.__junctions.values()
  
  def segments(self) -> ValuesView:
    return self.__segments.values()

  def get_junction(self, junction_toml_id: Tag) -> Junction:
    if junction_toml_id in self.__junctions:
      return self.__junctions[junction_toml_id]
    else:
      raise Exception(f'NavigationMesh does not have a junction with ID = {junction_toml_id}.')
  
  def get_segment(self, segment_toml_id: Tag) -> Segment:
    if segment_toml_id in self.__segments:
      return self.__segments[segment_toml_id]
    else:
      raise Exception(f'NavigationMesh does not have a segment with ID = {segment_toml_id}.')

  def find_junction(self, location: Point) -> Junction:
    if location in self.__junction_location_index:
      toml_id = self.__junction_location_index[location]
      return self.get_junction(toml_id)
    else:
      raise Exception(f'NavigationMesh does not have a junction at location {location}.')


  def find_segment(self, junction_id: str) -> Segment:
    if junction_id in self.__segments_junction_index:
      toml_id = self.__segments_junction_index[junction_id]
      return self.get_segment(toml_id)
    else:
      raise Exception(f'NavigationMesh does not have a segment with a junction ID of {junction_id}.')

  def find_connected_locations(self, junction_id: Tag) -> List[Point]:
    """Find all of the locations that can be directly reached from the junction."""
    segment = self.find_segment(junction_id)
    connected_locations: List[Point] = []
    for junction_id in segment.maps_to:
      connected_locations.append(self.get_junction(junction_id).location)
    return connected_locations