from __future__ import annotations

from typing import Callable, List, Optional, Tuple, Union
from abc import ABC, abstractmethod

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction, Orientation
from agents_playground.agents.structures import Point
from agents_playground.core.callable_utils import CallableUtility
  
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

AgentPath = List[AgentAction]