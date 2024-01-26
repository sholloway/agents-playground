# Geometry
from __future__ import annotations
from abc import abstractmethod
from typing import List
from agents_playground.spatial.polygon.polygon import Polygon
from agents_playground.spatial.polygon.polygon2d import Polygon2d
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vertex import Vertex, Vertex2d

class AABBox(Polygon):
  vertices: List[Vertex]

  @property
  @abstractmethod
  def min(self) -> Vertex:
    """Returns the smallest vertex on all axis."""
  
  @property
  @abstractmethod
  def max(self) -> Vertex:
    """Returns the smallest vertex on all axis."""

  @abstractmethod
  def point_in(self, point: Coordinate) -> bool:
    """Calculates if a given point is in the box."""

  # @abstractmethod
  # def intersects(self, aabb: AABBox) -> bool:
  #   """Intersection test between this and another AABBox"""

class AABBox2d(AABBox, Polygon2d):
  """
  A 2-dimensional bounding box.

  V3      V2
    -------
    |     |
    |     |
    -------
  V0      V1
  """
  def __init__(self, center: Vertex, half_width: float, half_height: float) -> None:
    self.vertices = [
      Vertex2d(x = center.coordinates[0] - half_width , y = center.coordinates[1] + half_height), # V0
      Vertex2d(x = center.coordinates[0] + half_width , y = center.coordinates[1] + half_height), # V1
      Vertex2d(x = center.coordinates[0] + half_width , y = center.coordinates[1] - half_height), # V2
      Vertex2d(x = center.coordinates[0] - half_width , y = center.coordinates[1] - half_height)  # V3
    ]

  @property
  def min(self) -> Vertex:
    """Returns the smallest vertex on both the X and Y axis."""
    return self.vertices[3]
  
  @property
  def max(self) -> Vertex:
    """Returns the largest vertex on both the X and Y axis."""
    return self.vertices[1]
  
  def point_in(self, point: Coordinate) -> bool:
    """Calculates if a given point is in the box."""
    return (self.min.coordinates[0] <= point.x and point.x <= self.max.coordinates[0]) \
      and (self.min.coordinates[1]  <= point.y and point.y <= self.max.coordinates[1])

class EmptyAABBox(AABBox2d):
  """Convince class for creating a bounding box with no size."""
  def __init__(self) -> None:
    super().__init__(
      center = Vertex2d(0,0),
      half_width= 0,
      half_height= 0
    )