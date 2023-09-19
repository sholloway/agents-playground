from __future__ import annotations
import math
from typing import Tuple, cast
from agents_playground.spatial.types import Coordinate, Radians

from agents_playground.spatial.vector import VECTOR_ROUNDING_PRECISION, Vector
from agents_playground.spatial.vertex import Vertex, Vertex2d

class Vector2d(Vector):
  """
  Represents a 2-dimensional vector.
  """

  def __init__(self, i: float, j: float) -> None:
    super().__init__()
    self._i = i
    self._j = j

  @property
  def i(self) -> float:
    return self._i
  
  @property
  def j(self) -> float:
    return self._j
  
  @property
  def k(self) -> float:
    return 0
  
  @staticmethod
  def from_vertices(vert_a: Vertex, vert_b: Vertex) -> Vector:
    """A factory method for creating a vector from two vertices.
    The direction of the vector is defined by vert_a - vert_a.
    """
    return Vector2d(
      i = vert_a.coordinates[0] - vert_b.coordinates[0],
      j = vert_a.coordinates[1] - vert_b.coordinates[1],
    )
  
  @staticmethod
  def from_points(start_point: Coordinate, end_point: Coordinate) -> Vector:
    """Create a new vector from two points
    The direction of the vector is defined by end_point - start_point.
    """
    return Vector2d(
      i = end_point.x - start_point.x, 
      j = end_point.y - start_point.y
    )
  
  def __eq__(self, other: object) -> bool:
    if isinstance(other, Vector2d):
      return self.to_tuple().__eq__(other.to_tuple())
    else:
      return self.to_tuple().__eq__(other)
    
  def __hash__(self) -> int:
    return hash(self.to_tuple())
  
  def __iter__(self):
    return iter(self.to_tuple())

  def scale(self, scalar: float) -> Vector:
    """Scale a vector by a scalar"""
    return Vector2d(self._i * scalar, self._j * scalar)

  def to_point(self, vector_origin: Coordinate) -> Coordinate:
    """Returns a point that is on the vector at the end of the vector.
    
    Args
      - vector_origin: The point that the vector starts at.

    Returns
      A point that is offset from the vector_origin by the vector.
    """
    return Coordinate(vector_origin.x + self._i, vector_origin.y + self._j)
  
  def to_vertex(self, vector_origin: Vertex) -> Vertex:
    """Returns a point that is on the vector at the end of the vector.
    
    Args
      - vector_origin: The point that the vector starts at.

    Returns
      A point that is offset from the vector_origin by the vector.
    """
    return Vertex2d(
      x = vector_origin.coordinates[0] + self._i, 
      y = vector_origin.coordinates[1] + self._j
    )

  def rotate(self, angle: Radians) -> Vector:
    """Create a new vector by rotating it by an angle around the Z axis.
    
    Args
      - angle: The angle to rotate by provided in Radians.

    Returns
      A new vector created by applying the rotation.
    """
    rounded_cosine = round(math.cos(angle), VECTOR_ROUNDING_PRECISION)
    rounded_sine = round(math.sin(angle), VECTOR_ROUNDING_PRECISION)
    return Vector2d(
      self._i * rounded_cosine- self._j * rounded_sine, 
      self._i * rounded_sine + self._j * rounded_cosine
    )

  def unit(self) -> Vector:
    """Returns the unit vector as a new vector."""
    l: float = self.length()
    return Vector2d(self._i/l, self._j/l)

  def length(self) -> float:
    """Calculates the length of the vector."""
    return math.sqrt(self._i**2 + self._j**2)

  def right_hand_perp(self) -> Vector:
    """Build a unit vector perpendicular to this vector."""
    # need to handle the special cases of when i or j are zero
    return Vector2d(self._j, -self._i).unit()
  
  def left_hand_perp(self) -> Vector:
    """Build a unit vector perpendicular to this vector."""
    # need to handle the special cases of when i or j are zero
    return Vector2d(-self._j, self._i).unit()
  
  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(i={self._i},j={self._j})'
  
  def dot(self, b: Vector) -> float:
    """Calculates the dot product between this vector and vector B."""
    return self._i * b.i + self._j * b.j
  
  def cross(self, b: Vector) -> Vector:
    """Calculates the cross product between this vector and vector B.
    
    Note: The cross product doesn't translate to 2D space. For dimension N
    it works with N-1 vectors. So for the use case of 2D the cross product is 
    returning the right-handed perpendicular value of vector B
    """
    return b.right_hand_perp()

  def project_onto(self, b: Vector) -> Vector:
    """Create a new vector by projecting this vector onto vector b.
    See: https://en.wikipedia.org/wiki/Vector_projection

    The new vector C is the same direction as vector B, but is the length 
    of the shadow of this vector "projected" onto vector B.
    C = dot(A, B)/squared(length(B)) * B
    """
    b_len_squared = b.i * b.i + b.j * b.j
    return b.scale(self.dot(b)/b_len_squared)
  
  def to_tuple(self) -> Tuple[float, ...]:
    """Creates a tuple from the vector."""
    return (self._i, self._j)