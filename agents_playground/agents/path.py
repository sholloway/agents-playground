from __future__ import annotations

from typing import Callable, List, Optional, Tuple, Union
from abc import ABC, abstractmethod
from math import cos, radians, sin 

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Vector2D
from agents_playground.core.callable_utils import CallableUtility
from agents_playground.core.types import Coordinate, Size
from agents_playground.simulation.tag import Tag
  
# Actions should modify agents. This will help decouple Agents 
# from knowing too much about the terrain.
# TODO: This probably needs to live in a different file.
class AgentAction(ABC):
  def __init__(self) -> None:
    super().__init__()
    self._before_action: Optional[Callable] = None
    self._after_action: Optional[Callable] = None

  def run(self, agent: Agent, **data) -> None:
    CallableUtility.invoke(self._before_action, data)
    self._perform(agent, **data)
    CallableUtility.invoke(self._after_action, data)

  @abstractmethod
  def _perform(self, agent: Agent, **data) -> None:
    """An instruction for an agent to do something."""

  @property
  def before_action(self) -> Optional[Callable]:
    return self._before_action

  @before_action.setter
  def before_action(self, action: Optional[Callable]) -> None:
    self._before_action = action
  
  @property
  def after_action(self) -> Optional[Callable]:
    return self._after_action

  @before_action.setter
  def after_action(self, action: Optional[Callable]) -> None:
    self._after_action = action

class AgentStep(AgentAction):
  """A waypoint in a path.
  
  A step represents a change in an agent along a path. This could be a 
  change in location or orientation or both.
  """
  def __init__(self, 
    location: Optional[Coordinate] = None, 
    orientation: Optional[Vector2D] = None) -> None:
    super().__init__()
    self._location: Optional[Coordinate] = location
    self._orientation: Optional[Vector2D] = orientation

  def _perform(self, agent: Agent, **data):
    """
    Implements AgentAction.perform.
    Moves the agent to an optional location and orientates the agent to an 
    optional direction.
    """
    if self._location :
      agent.move_to(self._location)
    if self._orientation:
      agent.face(self._orientation)

  @property
  def location(self) -> Optional[Coordinate]:
    return self._location

"""
What is Idle?
It is a path instruction that indicates the agent should 
not move for a certain number of frames.

How does this work if logic to do something is encapsulated in an Action?
"""
class IdleStep(AgentAction):
  frames: int
  def _perform(self, agent: Agent, **data):
    pass


class AgentPath:
  def __init__(self, id: Tag, steps: List[AgentAction] = []) -> None:
    self._steps: List[AgentAction] = steps
    self._id: Tag = id

  @property
  def id(self) -> Tag:
    return self._id

  def step(self, step_index: int) -> AgentAction:
    return self._steps[step_index]

  def __iter__(self):
    return self._steps.__iter__()

  def __next__(self):
    return self._steps.__next__()

  def __len__(self) -> int:
    return len(self._steps)  

class InterpolatedPath:
  def __init__(self, id: Tag, renderer: Callable, toml_id: Tag = None) -> None:
    self._id = id
    self._renderer = renderer
    self._toml_id = toml_id

  @property
  def id(self) -> Tag:
    return self._id
  
  @property
  def toml_id(self) -> Tag:
    return self._toml_id


  def render(self, cell_size: Size, offset: Size) -> None:
    self._renderer(self, cell_size, offset)

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
    control_points: Tuple[Union[int, float],...], 
    renderer: Callable, 
    closed: bool =True, 
    toml_id: Tag = None) -> None:
    super().__init__(id, renderer, toml_id)
    self._cp: Tuple[Union[int, float], ...] = control_points
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

  def direction(self, segment: int) -> Vector2D:
    # TODO: It may be better to return the unit vector here.
    p0, p1 = self.segment(segment)
    return Vector2D(p1[0] - p0[0], p1[1] - p0[1])

class CirclePath(InterpolatedPath):
  """Create a looping path in the shape of a circle."""
  def __init__(
    self, 
    id: Tag, 
    center: Tuple[float, float], 
    radius: Union[float, int], 
    renderer: Callable,
    toml_id: Tag = None
  ) -> None:
    super().__init__(id, renderer, toml_id)
    self._center = center
    self._radius = radius

  @property
  def center(self) -> Tuple[float, float]:
    return self._center

  @property
  def radius(self) -> Union[float, int]:
    return self._radius

  def interpolate(self, degree: float) -> Tuple[float, float]:
    """Finds a point on the circle.
    Args:
      - degree: The amount in degrees [0, 360] to interpolate. 

    Returns:
      A tuple of the point on the circle at (x,y) where the circle is located 
      at (a,b) with a radius of r:
        x = a + r* cos(t)
        y = b + r * sin(t)
    """
    rad = radians(degree)
    x = self._center[0] + self._radius * cos(rad)
    y = self._center[1] + self._radius * sin(rad)
    return (x,y)

  def tangent(self, point: Tuple[float, float], direction: int = 1) -> Vector2D:
    """ Find a unit vector tangent to the circle.

    Args:
      - point: The point at which to find the tangent.
      - direction: Which way the tangent should point. 1 for counter clockwise and - 1 for clockwise.

    Returns:
      A unit vector tangent to the circle at the given point.
    """
    # Find the direction vector
    dir_vector = Vector2D(point[0] - self._center[0], point[1] - self._center[1])
    dir_unit: Vector2D = dir_vector.unit()

    # Return this for a sec. I expect the triangles to always point away 
    # from the center.
    return dir_unit.left_hand_perp() if direction == 1 else dir_unit.right_hand_perp()