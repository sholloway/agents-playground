from abc import abstractmethod
from typing import Tuple
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.types import Radians
from agents_playground.spatial.vector.vector import Vector, VectorType
from agents_playground.spatial.vertex import Vertex


class Vector4d(Vector):
    def __init__(self, *components: VectorType) -> None:
        super().__init__(components)

    def new(self, *args: VectorType) -> Vector[VectorType]:
        """Create a new vector with the same shape but with the provided data."""
        return Vector4d(*args)

    @staticmethod
    def from_vertices(vert_a: Vertex, vert_b: Vertex) -> Vector:
        """A factory method for creating a vector from two vertices.
        The direction of the vector is defined by vert_a - vert_a.
        """
        # This doesn't make sense in 4D.
        raise NotImplementedError()

    def scale(self, scalar: float) -> Vector:
        """Scale a vector by a scalar"""
        raise NotImplementedError()

    def rotate(self, angle: Radians) -> Vector:
        """Create a new vector by rotating it by an angle.

        Args
          - angle: The angle to rotate by provided in Radians.

        Returns
          A new vector created by applying the rotation.
        """
        raise NotImplementedError()

    def right_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""
        raise NotImplementedError()

    def left_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""
        raise NotImplementedError()

    def cross(self, b: Vector) -> Vector:
        """Calculates the cross product between this vector and vector B."""
        raise NotImplementedError()
