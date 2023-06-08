from typing import Callable, Tuple
from agents_playground.core.types import Size
from agents_playground.paths.interpolated_path import InterpolatedPath
from agents_playground.simulation.tag import Tag
from agents_playground.spatial.vector2d import Vector2d

class LinearPath(InterpolatedPath):
  """An interpolation based bath.
  
  A path is composed of segments. Each segment has two control points.
  The control points are immutable.

  If there are N control points, then there are N - 1 segments.

  Example:
    p = Path((0,1,2,3,4,5,6,7,8,9))
  """
  def __init__(self, 
    id: Tag, 
    control_points: Tuple[int | float, ...], 
    renderer: Callable, 
    closed: bool =True, 
    toml_id: Tag = None) -> None:
    super().__init__(id, renderer, toml_id)
    self._cp: Tuple[int | float, ...] = control_points
    self._closed = closed

  @property
  def closed(self) -> bool:
    return self._closed
  
  @closed.setter
  def closed(self, looped: bool) -> None:
    self._closed = looped

  def interpolate(self, segment: int, u: float, a: float = 0, b: float = 1.0) -> Tuple[float, float]:
    """ Find a point(x,y) on the path using interpolation.

    For linear paths, interpolation is done between two points via:
    p(t) = (1 - t)*p0 + t* p1
    
    Where t is in the set [0,1]. If a different set is needed for t, 
    Then it can be projected to [0,1] by:
    t = (u - a)/(b - a)
    Args:
      - segment: Which segment on the path to interpolate on.
      - u: Often referred to as "time" on the line. It is in the set [a,b]
      - a: The lower bound of u. Default of 0. 
      - b: The upper bound of u. Default of 1.0.
    """
    p0, p1 = self.segment(segment)
    t = (u - a)/(b - a)
    diff = 1 - t
    return (p0[0] * diff + p1[0]*t, p0[1] * diff + p1[1]*t)

  def segment(self, seg_index: int) -> Tuple[Tuple[float, ...], Tuple[float,...]]:
    """Find the endpoints of a segment.
    
    Args:
      - seg_index: The index of the segment. Starting at 1. 
        
    Returns
      Returns a tuples of the form ((p0x, p0y), (p1x, p1y)).
    """
    d = seg_index * 2
    return self._cp[d-2:d], self._cp[d:d+2]

  def segments_count(self) -> int:
    """Returns the number of segments the path has.
    A path has #CP - 1 segments
    """
    return self.control_points_count() - 1

  def control_points_count(self) -> int:
    """Return the number of control points."""
    return int(len(self._cp) / 2)
    
  def control_points(self):
    """Iterator that returns the control points."""
    for p in range(0, len(self._cp), 2):
      yield self._cp[p], self._cp[p+1]

  def render(self, cell_size: Size, offset: Size) -> None:
    self._renderer(self, cell_size, offset, self._closed)

  def direction(self, segment: int) -> Vector2d:
    # TODO: It may be better to return the unit vector here.
    p0, p1 = self.segment(segment)
    return Vector2d(p1[0] - p0[0], p1[1] - p0[1])
