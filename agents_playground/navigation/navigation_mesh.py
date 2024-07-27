from argparse import Namespace
from types import SimpleNamespace
from typing import Dict, ValuesView

from agents_playground.simulation.tag import Tag
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()

Junction = SimpleNamespace


class NavigationMesh:
    def __init__(self) -> None:
        self._junctions: Dict[Tag, Junction] = dict()
        self._junction_location_index: Dict[Coordinate, Tag] = dict()

    def __del__(self) -> None:
        logger.info("NavigationMesh is deleted.")

    def purge(self) -> None:
        self._junctions.clear()
        self._junction_location_index.clear()

    def add_junction(self, junction: Junction) -> None:
        if junction.toml_id in self._junctions:
            raise Exception(
                f"The junction {junction.toml_id} is already defined in the navigation mesh."
            )
        else:
            self._junctions[junction.toml_id] = junction
            self._junction_location_index[junction.location] = junction.toml_id

    def junctions(self) -> ValuesView:
        return self._junctions.values()

    def get_junction_by_toml_id(self, junction_toml_id: Tag) -> Junction:
        if junction_toml_id in self._junctions:
            return self._junctions[junction_toml_id]
        else:
            raise Exception(
                f"NavigationMesh does not have a junction with TOML ID = {junction_toml_id}."
            )

    def get_junction_by_location(self, location: Coordinate) -> Junction:
        if location in self._junction_location_index:
            toml_id = self._junction_location_index[location]
            return self.get_junction_by_toml_id(toml_id)
        else:
            raise Exception(
                f"NavigationMesh does not have a junction at location {location}."
            )
