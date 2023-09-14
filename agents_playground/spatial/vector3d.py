from __future__ import annotations
import math
from typing import Tuple
from agents_playground.spatial.types import Coordinate, Radians

from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vertex import Vertex, Vertex3d

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
  
  @staticmethod
  def from_vertices(vert_a: Vertex, vert_b: Vertex) -> Vector:
    """A factory method for creating a vector from two vertices.
    The direction of the vector is defined by vert_a - vert_a.
    """
    return Vector3d(
      i = vert_a.coordinates[0] - vert_b.coordinates[0],
      j = vert_a.coordinates[1] - vert_b.coordinates[1],
      k = vert_a.coordinates[2] - vert_b.coordinates[2],
    )
  
  @staticmethod
  def from_points(start_point: Coordinate, end_point: Coordinate) -> Vector:
    """Create a new vector from two points
    The direction of the vector is defined by end_point - start_point.
    """
    # This doesn't make sense in 3D. Coordinates are for the 2D grid.
    raise NotImplemented()
  
  def __eq__(self, other: object) -> bool:
    if isinstance(other, Vector3d):
      return self.to_tuple().__eq__(other.to_tuple())
    else:
      return self.to_tuple().__eq__(other)
    
  def __hash__(self) -> int:
    return hash(self.to_tuple())

  def scale(self, scalar: float) -> Vector:
    """Scale a vector by a scalar"""
    return Vector3d(self._i * scalar, self._j * scalar, self._k * scalar)


  def to_point(self, vector_origin: Coordinate) -> Coordinate:
    """Returns a point that is on the vector at the end of the vector.
    
    Args
      - vector_origin: The point that the vector starts at.

    Returns
      A point that is offset from the vector_origin by the vector.
    """
    # This doesn't make sense in 3D. Coordinates are for the 2D grid.
    raise NotImplemented()
  
  def to_vertex(self, vector_origin: Vertex) -> Vertex:
    """Returns a point that is on the vector at the end of the vector.
    
    Args
      - vector_origin: The point that the vector starts at.

    Returns
      A point that is offset from the vector_origin by the vector.
    """
    return Vertex3d(
      x = vector_origin.coordinates[0] + self._i, 
      y = vector_origin.coordinates[1] + self._j,
      z = vector_origin.coordinates[2] + self._k,
    )

  """
  TODO 3D Vector Transformations
  - Decide if using righ-handed coordinates or left handed coordinates
    for 3D transformations. 
  - It may make more sense to implement all of the transformations as a compute
    shader or as part of the shaders.
  - For left handed algorithm, use the method provided in the book 
    Physically Based Rendering on page 83.  I previously implemented this 
    in the jitterbug-scala code base.
    https://github.com/sholloway/jitterbug-scala/blob/naive_whitted_raytracer/src/main/scala/org/jitterbug/math/three/Transformation3d.scala
  - What should the contract be?
    One thought is to have the Vector protocol define rotation like this.
    def rotate(self, angle: Radians, axis: Vector = Axis.Z)
      ...
    
    This contract would enable the existing 2D rotation.
  """
  def rotate(self, angle: Radians) -> Vector:
    """Create a new vector by rotating it by an angle.
    
    Args
      - angle: The angle to rotate by provided in Radians.

    Returns
      A new vector created by applying the rotation.
    """
    raise NotImplemented()
  

  def unit(self) -> Vector:
    """Returns the unit vector as a new vector."""
    raise NotImplemented()

  def length(self) -> float:
    """Calculates the length of the vector."""
    raise NotImplemented()

  def right_hand_perp(self) -> Vector:
    """Build a unit vector perpendicular to this vector."""
    # need to handle the special cases of when i or j are zero
    raise NotImplemented()
  
  def left_hand_perp(self) -> Vector:
    """Build a unit vector perpendicular to this vector."""
    # need to handle the special cases of when i or j are zero
    raise NotImplemented()
  
  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(i={self._i},j={self._j}, k={self._k})'
  
  def dot(self, b: Vector) -> float:
    """Calculates the dot product between this vector and vector B."""
    raise NotImplemented()
  
  def cross(self, b: Vector) -> Vector:
    """Calculates the cross product between this vector and vector B.
    
    Note: The cross product doesn't translate to 2D space. For dimension N
    it works with N-1 vectors. So for the use case of 2D the cross product is 
    returning the right-handed perpendicular value of vector B
    """
    raise NotImplemented()

  def project_onto(self, b: Vector) -> Vector:
    """Create a new vector by projecting this vector onto vector b.
    See: https://en.wikipedia.org/wiki/Vector_projection

    The new vector C is the same direction as vector B, but is the length 
    of the shadow of this vector "projected" onto vector B.
    C = dot(A, B)/squared(length(B)) * B
    """
    raise NotImplemented()
  
  def to_tuple(self) -> Tuple[float, ...]:
    """Creates a tuple from the vector."""
    return (self._i, self._j, self._k)