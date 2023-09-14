from __future__ import annotations
from abc import abstractmethod

from typing import Protocol, Tuple

from agents_playground.spatial.types import Coordinate, Radians
from agents_playground.spatial.vertex import Vertex

VECTOR_ROUNDING_PRECISION: int = 8

class Vector(Protocol):
  """
  Represents the contract for a vector.
  """

  @property
  @abstractmethod
  def i(self) -> float:
    """Returns the i component of the vector."""
  
  @property
  @abstractmethod
  def j(self) -> float:
    """Returns the j component of the vector."""
  
  @property
  @abstractmethod
  def k(self) -> float:
    """Returns the k component of the vector."""

  @staticmethod
  @abstractmethod
  def from_vertices(vert_a: Vertex, vert_b: Vertex) -> Vector:
    """A factory method for creating a vector from two vertices.
    The direction of the vector is defined by vert_a - vert_a.
    """

  @abstractmethod
  def scale(self, scalar: float) -> Vector:
    """Scale a vector by a scalar"""

  @abstractmethod
  def to_point(self, vector_origin: Coordinate) -> Coordinate:
    """Returns a point that is on the vector at the end of the vector.
    
    Args
      - vector_origin: The point that the vector starts at.

    Returns
      A point that is offset from the vector_origin by the vector.
    """
  
  @abstractmethod
  def to_vertex(self, vector_origin: Vertex) -> Vertex:
    """Returns a point that is on the vector at the end of the vector.
    
    Args
      - vector_origin: The point that the vector starts at.

    Returns
      A point that is offset from the vector_origin by the vector.
    """
    
  @abstractmethod
  def rotate(self, angle: Radians) -> Vector:
    """Create a new vector by rotating it by an angle.
    
    Args
      - angle: The angle to rotate by provided in Radians.

    Returns
      A new vector created by applying the rotation.
    """

  @abstractmethod
  def unit(self) -> Vector:
    """Returns the unit vector as a new vector."""

  @abstractmethod
  def length(self) -> float:
    """Calculates the length of the vector."""

  @abstractmethod
  def right_hand_perp(self) -> Vector:
    """Build a unit vector perpendicular to this vector."""
  
  @abstractmethod
  def left_hand_perp(self) -> Vector:
    """Build a unit vector perpendicular to this vector."""
    
  @abstractmethod
  def project_onto(self, b: Vector) -> Vector:
    """Create a new vector by projecting this vector onto vector B.
    See: https://en.wikipedia.org/wiki/Vector_projection

    The new vector C is the same direction as vector B, but is the length 
    of the shadow of this vector "projected" onto vector B.
    C = dot(A, B)/squared(length(B)) * B
    """

  @abstractmethod
  def dot(self, b: Vector) -> float:
    """Calculates the dot product between this vector and vector B."""
  
  @abstractmethod
  def cross(self, b: Vector) -> Vector:
    """Calculates the cross product between this vector and vector B."""

  @abstractmethod
  def to_tuple(self) -> Tuple[float, ...]:
    """Creates a tuple from the vector."""

  @abstractmethod
  def __hash__(self) -> int:
    """Return the hash value of the vector."""
  