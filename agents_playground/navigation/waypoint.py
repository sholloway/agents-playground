from __future__ import annotations
from typing import Optional

from numpy import str0

from agents_playground.agents.structures import Point

NavigationCost = float

class Waypoint:
  """A decorator class that wraps a Point to enable chaining points."""
  def __init__(self, point: Point, predecessor: Waypoint = None):
    self._point = point
    self.__predecessor: Optional[Waypoint] = predecessor
    self.__cost_from_start: NavigationCost = 0
    self.__cost_to_target: NavigationCost = 0

  @property
  def point(self) -> Point:
    return self._point

  @property
  def predecessor(self) -> Optional[Waypoint]:
    return self.__predecessor
  
  @predecessor.setter
  def predecessor(self, predecessor: Waypoint) -> None:
    self.__predecessor = predecessor

  @property 
  def cost_from_start(self) -> NavigationCost:
    return self.__cost_from_start
  
  @cost_from_start.setter 
  def cost_from_start(self, cost: NavigationCost) -> None:
    self.__cost_from_start = cost
  
  @property 
  def cost_to_target(self) -> NavigationCost:
    return self.__cost_to_target
  
  @cost_to_target.setter 
  def cost_to_target(self, cost: NavigationCost) -> None:
    self.__cost_to_target = cost
    
  def total_cost(self) -> NavigationCost:
    return self.cost_from_start + self.cost_to_target

  def __str__(self) -> str:
    pred_str = f'({self.__predecessor.point.x}, {self.__predecessor.point.y})' if self.__predecessor else 'None'
    return f'Waypoint (x = {self.point.x}, y = {self.point.y}) with predecessor {pred_str}'

  def __repr__(self) -> str:
    return self.__str__()

  def __eq__(self, other: object) -> bool:
    """For equality checks, only consider the decorated point, not the predecessor."""
    if (isinstance(other, Waypoint)):
      return self.point.x == other.point.x and self.point.y == other.point.y
    return False

  def __hash__(self) -> int:
    return self.point.__hash__()