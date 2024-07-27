from typing import Protocol
from agents_playground.spatial.polygon.polygon import Polygon


class Polygon3d(Polygon, Protocol):
    """
    A lattice of 3D vertices.

    The vertices are wound counter-clockwise (CCW).
    """

    def intersect(self, other: Polygon) -> bool:
        """An intersection test between this polygon and another.

        Args:
          - other: The polygon to check for overlap with.

        Return:
          Returns True if the two polygons intersect.
        """
        return False
