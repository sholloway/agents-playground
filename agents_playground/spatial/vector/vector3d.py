from __future__ import annotations
import math
from typing import Tuple, cast

from deprecated import deprecated  # type: ignore

from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.types import Radians
from agents_playground.spatial.vector.vector import (
    Vector,
    NumericType,
)
from agents_playground.spatial.vertex import Vertex


class Vector3d(Vector):
    """Represents a 3-dimensional vector."""

    def __init__(self, *components: NumericType):
        super().__init__(components)

    def new(self, *args: NumericType) -> Vector[NumericType]:
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
            cast(float, end_point[0] - start_point[0]),
            cast(float, end_point[1] - start_point[1]),
            cast(float, end_point[2] - start_point[2]),
        )

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

    def cross(self: Vector, b: Vector) -> Vector:
        """Calculates the cross product between this vector and vector B."""
        return Vector3d(
            self.j * b.k - self.k * b.j,
            self.k * b.i - self.i * b.k,
            self.i * b.j - self.j * b.i,
        )
