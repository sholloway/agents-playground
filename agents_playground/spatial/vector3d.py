from __future__ import annotations
import math

from agents_playground.spatial.vector import Vector

class Vector3d(Vector):
  """Represents a 3-dimensional vector."""
  def __init__(self, i: float, j: float, k: float) -> None:
    super().__init__()
    self._i = i
    self._j = j
    self._k = k

  @property
  def i(self) -> float:
    return self._i
  
  @property
  def j(self) -> float:
    return self._j
  
  @property
  def k(self) -> float:
    return self._k