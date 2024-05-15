from abc import abstractmethod
from typing import Tuple
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.types import Radians
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vertex import Vertex


class Vector4d(Vector):
    def __init__(self, i: float, j: float, k: float, w: float) -> None:
        super().__init__()
        self._i = i
        self._j = j
        self._k = k
        self._w = w

    @property
    def i(self) -> float:
        return self._i

    @property
    def j(self) -> float:
        return self._j

    @property
    def k(self) -> float:
        return self._k

    @property
    def w(self) -> float:
        return self._w

    @i.setter
    def i(self, other: float) -> None:
        """Sets the i component of the vector."""
        self._i = other

    @j.setter
    def j(self, other: float) -> None:
        """Sets the j component of the vector."""
        self._j = other

    @k.setter
    def k(self, other: float) -> None:
        """Sets the j component of the vector."""
        self._k = other

    @w.setter
    def w(self, other: float) -> None:
        """Sets the w component of the vector."""
        self._w = other

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

    def to_point(self, vector_origin: Coordinate) -> Coordinate:
        """Returns a point that is on the vector at the end of the vector.

        Args
          - vector_origin: The point that the vector starts at.

        Returns
          A point that is offset from the vector_origin by the vector.
        """
        raise NotImplementedError()

    def to_vertex(self, vector_origin: Vertex) -> Vertex:
        """Returns a point that is on the vector at the end of the vector.

        Args
          - vector_origin: The point that the vector starts at.

        Returns
          A point that is offset from the vector_origin by the vector.
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    def length(self) -> float:
        """Calculates the length of the vector."""
        raise NotImplementedError()

    def right_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""
        raise NotImplementedError()

    def left_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""
        raise NotImplementedError()

    def project_onto(self, b: Vector) -> Vector:
        """Create a new vector by projecting this vector onto vector B.
        See: https://en.wikipedia.org/wiki/Vector_projection

        The new vector C is the same direction as vector B, but is the length
        of the shadow of this vector "projected" onto vector B.
        C = dot(A, B)/squared(length(B)) * B
        """
        raise NotImplementedError()

    def dot(self, b: Vector) -> float:
        """Calculates the dot product between this vector and vector B."""
        return self._i * b.i + self._j * b.j + self._k * b.k + self._w * b.w

    def __mul__(self, other: Vector) -> float:
        """Enables using the * operator for the dot product."""
        return self.dot(other)

    def __sub__(self, other: Vector) -> Vector:
        """Enables using the - operator for vector subtraction."""
        return Vector4d(
            self.i - other.i, self.j - other.j, self.k - other.k, self.w - other.w
        )

    def cross(self, b: Vector) -> Vector:
        """Calculates the cross product between this vector and vector B."""
        raise NotImplementedError()

    def to_tuple(self) -> Tuple[float, ...]:
        """Creates a tuple from the vector."""
        return (self._i, self._j, self._k, self._w)

    def __hash__(self) -> int:
        """Return the hash value of the vector."""
        return hash(self.to_tuple())

    def __iter__(self):
        return iter(self.to_tuple())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector4d):
            return self.to_tuple().__eq__(other.to_tuple())
        else:
            return self.to_tuple().__eq__(other)
