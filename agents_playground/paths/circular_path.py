from math import cos, radians, sin 
from typing import Callable, Tuple

from agents_playground.paths.interpolated_path import InterpolatedPath
from agents_playground.simulation.tag import Tag
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vector.vector2d import Vector2d

class CirclePath(InterpolatedPath):
  """Create a looping path in the shape of a circle."""
  def __init__(
    self, 
    id: Tag, 
    center: Tuple[float, float], 
    radius: float | int, 
    renderer: Callable,
    toml_id: Tag
  ) -> None:
    super().__init__(id, renderer, toml_id)
    self._center = center
    self._radius = radius

  @property
  def center(self) -> Tuple[float, float]:
    return self._center

  @property
  def radius(self) -> float | int:
    return self._radius

  def interpolate(self, degree: float) -> Tuple[float, float]:
    """Finds a point on the circle.
    Args:
      - degree: The amount in degrees [0, 360] to interpolate. 

    Returns:
      A tuple of the point on the circle at (x,y) where the circle is located 
      at (a,b) with a radius of r:
        x = a + r * cos(t)
        y = b + r * sin(t)
    """
    rad = radians(degree)
    x = self._center[0] + self._radius * cos(rad)
    y = self._center[1] + self._radius * sin(rad)
    return (x,y)

  def tangent(self, point: Tuple[float, float], direction: int = 1) -> Vector:
    """ Find a unit vector tangent to the circle.

    Args:
      - point: The point at which to find the tangent.
      - direction: Which way the tangent should point. 1 for counter clockwise and - 1 for clockwise.

    Returns:
      A unit vector tangent to the circle at the given point.
    """
    # Find the direction vector
    dir_vector = Vector2d(point[0] - self._center[0], point[1] - self._center[1])
    dir_unit: Vector = dir_vector.unit()

    # Return this for a sec. I expect the triangles to always point away 
    # from the center.
    return dir_unit.left_hand_perp() if direction == 1 else dir_unit.right_hand_perp()