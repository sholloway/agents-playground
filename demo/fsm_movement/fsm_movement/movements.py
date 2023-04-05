from abc import abstractmethod
from math import radians
from typing import Callable, List, Protocol, Tuple
from agents_playground.agents.direction import Vector2d
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.core.types import Coordinate

from agents_playground.counter.counter import Counter
from agents_playground.paths.circular_path import CirclePath
from agents_playground.scene.scene import Scene


class Movement(Protocol):
  appropriate_states: List[str]
  active_counter: Counter

  def appropriate(self, state_name: str) -> bool:
    return state_name in self.appropriate_states

  def move(self, agent: AgentLike, scene: Scene) -> None:
    self._move(agent, scene)
    self.active_counter.decrement()

  def reset(self) -> None:
    self.active_counter.reset()
  
  @abstractmethod
  def _move(self, agent: AgentLike, scene: Scene) -> None:
    ...

class ClockwiseNavigation(Movement):
  def __init__(
    self, 
    path: CirclePath, 
    active_t: float, 
    speed: float, 
    frames_active: int, 
    expired_action: Callable
  ) -> None:
    self._path = path
    self._active_t = active_t
    self._max_degree = 360
    self.appropriate_states = ['NAVIGATING_CLOCKWISE']
    self._speed = speed
    self._direction = 1  # Positive is CW, negative is CCW.
    self.active_counter = Counter(start = frames_active, min_value = 0, min_value_reached = expired_action)

  def _move(self, agent: AgentLike, scene: Scene) -> None:
    pt: Tuple[float, float] = self._path.interpolate(self._active_t)
    agent.move_to(Coordinate(pt[0], pt[1]), scene.cell_size)
    tangent_vector: Vector2d = self._path.tangent(pt, self._direction)
    agent.face(tangent_vector)

    self._active_t += self._speed
    if self._active_t > self._max_degree:
      self._active_t = 0

class CounterClockwiseNavigation(Movement):
  def __init__(
    self, 
    path: CirclePath, 
    active_t: float, 
    speed: float, 
    frames_active: int, 
    expired_action: Callable
  ) -> None:
    self._path = path
    self._active_t = active_t
    self._max_degree = 360
    self.appropriate_states = ['NAVIGATING_CLOCKWISE']
    self._speed = speed
    self._direction = -1 # Positive is CW, negative is CCW.
    self.active_counter = Counter(start = frames_active, min_value = 0, min_value_reached = expired_action)

  def _move(self, agent: AgentLike, scene: Scene) -> None:
    pt: Tuple[float, float] = self._path.interpolate(self._active_t)
    agent.move_to(Coordinate(pt[0], pt[1]), scene.cell_size)
    tangent_vector: Vector2d = self._path.tangent(pt, self._direction)
    agent.face(tangent_vector)

    self._active_t += self._speed
    if self._active_t > self._max_degree:
      self._active_t = 0

class SpinningClockwise(Movement):
  def __init__(
    self, 
    frames_active: int, 
    expired_action: Callable,
    rotation_amount: float = radians(5)
  ) -> None:
    self.appropriate_states = ['SPINNING_CW']
    self.active_counter = Counter(start = frames_active, min_value = 0, min_value_reached = expired_action)
    self._direction = 1
    self._rotation_amount = rotation_amount

  def _move(self, agent: AgentLike, scene: Scene) -> None:
    new_orientation = agent.position.facing.rotate(self._rotation_amount * self._direction)
    agent.face(new_orientation)

class SpinningCounterClockwise(Movement):
  def __init__(
    self, 
    frames_active: int, 
    expired_action: Callable,
    rotation_amount: float = radians(5)
  ) -> None:
    self.appropriate_states = ['SPINNING_CC']
    self.active_counter = Counter(start = frames_active, min_value = 0, min_value_reached = expired_action)
    self._direction = -1
    self._rotation_amount = rotation_amount

  def _move(self, agent: AgentLike, scene: Scene) -> None:
    new_orientation = agent.position.facing.rotate(self._rotation_amount * self._direction)
    agent.face(new_orientation)

class Pulsing(Movement):
  def __init__(
    self, 
    frames_active: int, 
    expired_action: Callable
  ) -> None:
    self.appropriate_states = ['PULSING']
    self.active_counter = Counter(start = frames_active, min_value = 0, min_value_reached = expired_action)

  def _move(self, agent: AgentLike, scene: Scene) -> None:
    pass