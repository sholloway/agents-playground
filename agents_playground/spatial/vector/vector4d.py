from agents_playground.spatial.types import Radians
from agents_playground.spatial.vector.vector import Vector, NumericType


class Vector4d(Vector):
    def __init__(self, *components: NumericType) -> None:
        super().__init__(components)

    def new(self, *args: NumericType) -> Vector[NumericType]:
        """Create a new vector with the same shape but with the provided data."""
        return Vector4d(*args)

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
