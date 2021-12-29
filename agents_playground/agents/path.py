from __future__ import annotations
from typing import List, Optional, Tuple, Union
from abc import ABC, abstractmethod

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction, Orientation
from agents_playground.agents.structures import Point

# Actions should modify agents. This will help decouple Agents 
# from knowing too much about the terrain.
class AgentAction(ABC):
  @abstractmethod
  def perform(self, agent: Agent):
    """An instruction for an agent to do something."""

"""
What is a step in a path?
- A step indicates a change.
- A change in: location.
- A change in: orientation.
- Multiple changes
"""
class AgentStep(AgentAction):
  def __init__(self, 
    location: Optional[Point] = None, 
    orientation: Optional[Direction] = None) -> None:
      super().__init__()
      self._location: Optional[Point] = location
      self._orientation: Optional[Direction] = orientation

  def perform(self, agent: Agent):
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
  def perform(self, agent: Agent):
    pass

AgentPath = List[AgentAction]