from __future__ import annotations

from abc import abstractmethod
from typing import List
from agents_playground.spatial.polygon.polygon import Polygon
from agents_playground.spatial.coordinate import Coordinate


class AABBox(Polygon):
    vertices: List[Coordinate]

    @property
    @abstractmethod
    def min(self) -> Coordinate:
        """Returns the smallest vertex on all axis."""

    @property
    @abstractmethod
    def max(self) -> Coordinate:
        """Returns the largest vertex on all axis."""

    @abstractmethod
    def point_in(self, point: Coordinate) -> bool:
        """Calculates if a given point is in the box."""

    @abstractmethod
    def intersects(self, aabb: AABBox) -> bool:
      """Intersection test between this and another AABBox"""

class EmptyAABBox(AABBox):
    """Convince class for creating a bounding box with no size."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def min(self) -> Coordinate:
        """Returns the smallest vertex on all axis."""
        return Coordinate(0.0)

    @property
    def max(self) -> Coordinate:
        """Returns the smallest vertex on all axis."""
        return Coordinate(0.0)

    
    def point_in(self, point: Coordinate) -> bool:
        """Calculates if a given point is in the box."""
        return False

    
    def intersects(self, aabb: AABBox) -> bool:
        """Intersection test between this and another AABBox"""
        return False
    
    def intersect(self, other: Polygon) -> bool:
        """An intersection test between this polygon and another.

        Args:
          - other: The polygon to check for overlap with.

        Return:
          Returns True if the two polygons intersect.
        """
        return False