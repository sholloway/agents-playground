from __future__ import annotations
import math
from typing import Tuple

from deprecated import deprecated

from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.types import Radians
from agents_playground.spatial.vector.vector import VECTOR_ROUNDING_PRECISION, Vector, VectorType
from agents_playground.spatial.vertex import Vertex, Vertex3d


class Vector3d(Vector):
    """Represents a 3-dimensional vector."""

    def __init__(self, *components: VectorType) -> None:
        super().__init__(components)

    def new(self, *args: VectorType) -> Vector[VectorType]:
        """Create a new vector with the same shape but with the provided data."""
        return Vector3d(*args)

    @deprecated(reason="Use coordinates rather than the vertex object.")
    @staticmethod
    def from_vertices(vert_a: Vertex, vert_b: Vertex) -> Vector:
        """A factory method for creating a vector from two vertices.
        The direction of the vector is defined by vert_a - vert_b.
        """
        return Vector3d(
            vert_a.coordinates[0] - vert_b.coordinates[0],
            vert_a.coordinates[1] - vert_b.coordinates[1],
            vert_a.coordinates[2] - vert_b.coordinates[2],
        )

    @staticmethod
    def from_points(start_point: Coordinate, end_point: Coordinate) -> Vector:
        """Create a new vector from two points
        The direction of the vector is defined by end_point - start_point.
        """
        return Vector3d(
            i=end_point[0] - start_point[0],
            j=end_point[1] - start_point[1],
            k=end_point[2] - start_point[2],
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector3d):
            return self.to_tuple().__eq__(other.to_tuple())
        else:
            return self.to_tuple().__eq__(other)

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __iter__(self):
        return iter(self.to_tuple())

    def scale(self, scalar: float) -> Vector:
        """Scale a vector by a scalar"""
        return Vector3d(self._i * scalar, self._j * scalar, self._k * scalar)


    """
    TODO 3D Vector Transformations
    - Decide if using right-handed coordinates or left handed coordinates
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
        raise NotImplementedError()

    def unit(self) -> Vector:
        """Returns the unit vector as a new vector."""
        l: float = self.length()
        return Vector3d(self._i / l, self._j / l, self._k / l)

    def length(self) -> float:
        """Calculates the length of the vector."""
        return math.sqrt(self._i**2 + self._j**2 + self._k**2)

    # TODO: This doesn't make sense in 3D. Rather the general operation
    # should be to find a perpendicular vector in a given plane.
    def right_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""
        # need to handle the special cases of when i or j are zero
        raise NotImplementedError("This doesn't make sense in 3D.")

    # TODO: This doesn't make sense in 3D. Rather the general operation
    # should be to find a perpendicular vector in a given plane.
    def left_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""
        # need to handle the special cases of when i or j are zero
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(i={self._i},j={self._j}, k={self._k})"

    def dot(self, b: Vector) -> float:
        """Calculates the dot product between this vector and vector B."""
        return self._i * b.i + self._j * b.j + self._k * b.k

    def __mul__(self, other: Vector) -> float:
        """Enables using the * operator for the dot product."""
        return self.dot(other)

    def __sub__(self, other: Vector) -> Vector:
        """Enables using the - operator for vector subtraction."""
        return Vector3d(self.i - other.i, self.j - other.j, self.k - other.k)

    def cross(self, b: Vector) -> Vector:
        """Calculates the cross product between this vector and vector B."""
        return Vector3d(
            self._j * b.k - self._k * b.j,
            self._k * b.i - self._i * b.k,
            self._i * b.j - self._j * b.i,
        )

    def project_onto(self, b: Vector) -> Vector:
        """Create a new vector by projecting this vector onto vector b.
        See: https://en.wikipedia.org/wiki/Vector_projection

        The new vector C is the same direction as vector B, but is the length
        of the shadow of this vector "projected" onto vector B.
        C = dot(A, B)/squared(length(B)) * B = dot(A, B)/dot(B,B) * B
        """
        projected_distance: float = round(
            self.dot(b) / b.dot(b), VECTOR_ROUNDING_PRECISION
        )
        return b.scale(projected_distance)

    def to_tuple(self) -> Tuple[float, ...]:
        """Creates a tuple from the vector."""
        return (self._i, self._j, self._k)
