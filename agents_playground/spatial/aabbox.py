# Geometry
from agents_playground.spatial.types import Coordinate

class AABBox:
  """An axis-aligned bounding box."""
  def __init__(self, min: Coordinate, max: Coordinate) -> None:
    """ Creates an axis-aligned bounding box defined by two points.
    Args:
      - min: The left most, upper point.
      - max: The right most, lower point.
    """
    self._min: Coordinate = min
    self._max: Coordinate = max

  @property
  def min(self) -> Coordinate:
    return self._min
  
  @property
  def max(self) -> Coordinate:
    return self._max

  def point_in(self, point: Coordinate) -> bool:
    """Calculates if a given point is in the box."""
    return (self._min.x <= point.x and point.x <= self._max.x) \
      and (self._min.y <= point.y and point.y <= self._max.y)

  def __repr__(self) -> str:
    return f"""
    {self.__class__.__name__}
    min: {self._min}
    max: {self._max}
    """
  
class EmptyAABBox(AABBox):
  """Convince class for creating a bounding box with no size."""
  def __init__(self) -> None:
    super().__init__(Coordinate(0,0), Coordinate(0,0))