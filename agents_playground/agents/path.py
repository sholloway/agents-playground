from __future__ import annotations

from typing import Callable, List, Optional, Tuple, Union
from abc import ABC, abstractmethod

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction, Orientation
from agents_playground.agents.structures import Point
from agents_playground.core.callable_utils import CallableUtility
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
    location: Optional[Point] = None, 
    orientation: Optional[Direction] = None) -> None:
    super().__init__()
    self._location: Optional[Point] = location
    self._orientation: Optional[Direction] = orientation

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
  def location(self) -> Optional[Point]:
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

class Path:
  """An interpolation based bath.
  
  A path is composed of segments. Each segment has two control points.
  The control points are immutable.

  If there are N control points, then there are N - 1 segments.

  Example:
    p = Path((0,1,2,3,4,5,6,7,8,9))
  """
  def __init__(self, control_points: Tuple[Union[int, float]]) -> None:
    self._cp: Tuple[Union[int, float]] = control_points


  def interpolate(self, segment: int, t: float, a: float = 0, b: float = 1.0) -> Tuple[float, float]:
    """ Find a point(x,y) on the path using interpolation.

    Args:
      - segment: Which segment on the path to interpolate on.
      - t: Often referred to as "time" on the line. It is in the set [a,b]
      - a: The lower bound of t. Default of 0. 
      - b: The upper bound of t. Default of 1.0.
    """
    # For linear paths, interpolation is done between two points via:
    # p(t) = (1 - t)*p0 + t* p1
    # Where t is in the set [0,1]. If a different set is needed for t, 
    # Then it can be projected to [0,1] by:
    # t = (u - a)/(b - a)
    pass


  def segment(self, seg_index: int) -> Tuple[float]:
    """Find the endpoints of a segment.
    
    Args:
      - seg_index: The index of the segment. The 0 index returns the segment [pn, p0]

    Returns
      Returns a tuple of the form (p0x, p0y, p1x, p1y).
    """
    p0x = self._cp[seg_index * 2 - 2]
    p0y = self._cp[seg_index * 2 - 1]
    p1x = self._cp[seg_index * 2]
    p1y = self._cp[seg_index * 2 + 1]
    
    # TODO: Can I change this to use a slice?
    # Is a slice faster than 4 individual lookups?
    return (p0x, p0y, p1x, p1y)

  def __len__(self) -> int:
    """Returns the number of segments the path has.
    A path has #CP - 1 segments
    """
    return int(len(self._cp) / 2) - 1
