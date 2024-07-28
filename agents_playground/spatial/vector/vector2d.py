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

class Vector2d(Vector):
    """
    Represents a 2-dimensional vector.
    """

    def __init__(self, *components: NumericType) -> None:
        super().__init__(components)

    def new(self, *args: NumericType) -> Vector[NumericType]:
        """Create a new vector with the same shape but with the provided data."""
        return Vector2d(*args)

    @staticmethod
    def from_points(start_point: Coordinate, end_point: Coordinate) -> Vector:
        """Create a new vector from two points
        The direction of the vector is defined by end_point - start_point.
        """
        direction = end_point - start_point
        return Vector2d(cast(float, direction[0]), cast(float, direction[1]))

    def rotate(self, angle: Radians) -> Vector:
        """Create a new vector by rotating it by an angle around the Z axis.

        Args
          - angle: The angle to rotate by provided in Radians.

        Returns
          A new vector created by applying the rotation.
        """
        rounded_cosine = math.cos(angle)
        rounded_sine = math.sin(angle)
        return Vector2d(
            self.i * rounded_cosine - self.j * rounded_sine,
            self.i * rounded_sine + self.j * rounded_cosine,
        )

    def right_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""
        # need to handle the special cases of when i or j are zero
        return Vector2d(self.j, -self.i).unit()

    def left_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""
        # need to handle the special cases of when i or j are zero
        return Vector2d(-self.j, self.i).unit()

    def cross(self, b: Vector) -> Vector:
        """Calculates the cross product between this vector and vector B.

        Note: The cross product doesn't translate to 2D space. For dimension N
        it works with N-1 vectors. So for the use case of 2D the cross product is
        returning the right-handed perpendicular value of vector B
        """
        return b.right_hand_perp()
