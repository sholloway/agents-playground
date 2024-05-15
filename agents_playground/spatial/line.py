from typing import NamedTuple

from agents_playground.spatial.coordinate import Coordinate


class Line2d(NamedTuple):
    """A two dimensional line defined by its endpoints A and B."""

    a: Coordinate
    b: Coordinate
