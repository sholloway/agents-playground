from __future__ import annotations
from abc import ABC, abstractmethod
from decimal import Decimal
from fractions import Fraction
from itertools import starmap
import itertools
import math
from functools import reduce, wraps
from operator import add, mul, sub
from typing import Generic, Tuple, TypeVar, cast

from deprecated import deprecated  # type: ignore

from agents_playground.core.types import (
    NumericType,
    NumericTypeAlias,
    box_numeric_value,
    enforce_same_type,
)
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.types import Radians
from agents_playground.spatial.vertex import Vertex, Vertex2d, Vertex3d


class VectorError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def enforce_vector_size(func):
    """A decorator that guards against using another vector of a different size."""

    @wraps(func)
    def _guard(*args, **kwargs):
        self: Vector = args[0]
        other: Vector = args[1]
        if len(self) == len(other):
            return func(*args, **kwargs)
        else:
            error_msg = (
                f"Cannot perform this operation on vectors that are of different sizes.",
                f"len(self) == {len(self)}",
                f"len(other) == {len(other)}",
            )
            raise VectorError(error_msg)

    return _guard


def enforce_vector_type(func):
    """A decorator that guards against using another vector of a different type.
    Prevents mixing integers, floats, and fractions.
    """

    @wraps(func)
    def _guard(*args, **kwargs):
        self: Vector = args[0]
        other: Vector = args[1]

        # Look at the first type in this vector. If any of the types are different
        # raise an error.
        expected_type = type(self[0])
        for value in itertools.chain(self, other):
            if type(value) != expected_type:
                error_msg = (
                    "Cannot mix vectors of different types.",
                    f"Self expects type {expected_type}",
                    f"The other vector contained component of type {type(value)}",
                )
                raise VectorError(error_msg)

        return func(*args, **kwargs)

    return _guard


def box_result(func):
    """
    A decorator that boxes the result to have the same numeric
    type as the vector's components.
    """

    @wraps(func)
    def _guard(*args, **kwargs) -> NumericTypeAlias:
        self: Vector = args[0]
        original_type = type(self._components[0])
        initial_result = func(*args, **kwargs)
        match original_type.__name__:
            case "int":
                return int(initial_result)
            case "float":
                return float(initial_result)
            case "Decimal":
                return Decimal(initial_result)
            case "Fraction":
                return Fraction(initial_result)
            case _:
                raise VectorError(f"Unsupported type {original_type.__name__}.")

    return _guard


class Vector(Generic[NumericType], ABC):
    """
    Represents the contract for a vector.
    """

    def __init__(self, *components: NumericType) -> None:
        self._components: list[NumericType] = list(*components)

    @abstractmethod
    def new(self, *args: NumericType) -> Vector[NumericType]:
        """Create a new vector with the same shape but with the provided data."""

    @abstractmethod
    def cross(self: Vector, b: Vector) -> Vector:
        """Calculates the cross product between this vector and vector B."""

    # @deprecated(reason="Use coordinates rather than the vertex object.")
    # @abstractmethod
    # @staticmethod
    # def from_vertices(vert_a: Vertex, vert_b: Vertex) -> Vector:
    #     """A factory method for creating a vector from two vertices.
    #     The direction of the vector is defined by vert_a - vert_a.
    #     """

    @abstractmethod
    def rotate(self, angle: Radians) -> Vector:
        """Create a new vector by rotating it by an angle.

        Args
          - angle: The angle to rotate by provided in Radians.

        Returns
          A new vector created by applying the rotation.
        """

    @abstractmethod
    def right_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""

    @abstractmethod
    def left_hand_perp(self) -> Vector:
        """Build a unit vector perpendicular to this vector."""

    @property
    def i(self) -> NumericType:
        """Returns the I component of the vector."""
        return self._components[0]

    @i.setter
    def i(self, other: NumericType) -> None:
        """Sets the I component of the vector."""
        self._components[0] = other

    @property
    def j(self) -> NumericType:
        """Returns the J component of the vector."""
        return self._components[1]

    @j.setter
    def j(self, other: NumericType) -> None:
        """Sets the J component of the vector."""
        self._components[1] = other

    @property
    def k(self) -> NumericType:
        """Returns the K component of the vector."""
        if len(self._components) > 2:
            return self._components[2]
        return 0  # type: ignore

    @k.setter
    def k(self, other: NumericType) -> None:
        """Sets the K component of the vector."""
        if len(self._components) > 2:
            self._components[2] = other
        else:
            raise NotImplementedError()

    @property
    def w(self) -> NumericType:
        """Returns the W component of the vector."""
        if len(self._components) > 3:
            return self._components[3]
        return 0  # type: ignore

    @w.setter
    def w(self, other: NumericType) -> None:
        """Sets the W component of the vector."""
        if len(self._components) > 3:
            self._components[3] = other
        else:
            raise NotImplementedError()

    def __len__(self) -> int:
        return len(self._components)

    def __repr__(self) -> str:
        t = self.to_tuple()
        return f"Vector{len(t)}d({','.join(map(str, t))})"

    def scale(self, scalar: NumericType) -> Vector[NumericType]:
        """Scale a vector by a scalar."""
        new_components = [component * scalar for component in self._components]
        return self.new(*new_components)

    def to_point(self, vector_origin: Coordinate) -> Coordinate:
        """Returns a point that is on the vector at the end of the vector.

        Args
          - vector_origin: The point that the vector starts at.

        Returns
          A point that is offset from the vector_origin by the vector.
        """
        if len(vector_origin) == len(self):
            new_components = []
            for index, component in enumerate(self._components):
                new_components.append(component + vector_origin[index])  # type: ignore
            return Coordinate(*new_components)
        else:
            error_msg = (
                "Cannot offset a vector to a coordinate that has a different dimension.",
                f"Vector has {len(self)} components.",
                f"The coordinate has {len(vector_origin)} components.",
            )
            raise VectorError(error_msg)

    @deprecated(reason="Use to_point. Vertex is deprecated.")
    def to_vertex(self, vector_origin: Vertex) -> Vertex:
        """Returns a point that is on the vector at the end of the vector.

        Args
          - vector_origin: The point that the vector starts at.

        Returns
          A point that is offset from the vector_origin by the vector.
        """
        if len(vector_origin) == len(self):
            new_components = []
            for index, component in enumerate(self._components):
                new_components.append(component + vector_origin.coordinates[index])  # type: ignore

            if isinstance(vector_origin, Vertex2d):
                return Vertex2d(new_components[0], new_components[1])
            elif isinstance(vector_origin, Vertex3d):
                return Vertex3d(new_components[0], new_components[1], new_components[2])
            else:
                raise VectorError("Unsupported vertex type.")
        else:
            error_msg = (
                "Cannot offset a vector to a coordinate that has a different dimension.",
                f"Vector has {len(self)} components.",
                f"The coordinate has {len(vector_origin)} components.",
            )
            raise VectorError(error_msg)

    def unit(self: Vector[NumericType]) -> Vector[NumericType]:
        """Returns the unit vector as a new vector."""
        length: NumericTypeAlias = self.length()
        new_components: list = [c / length for c in self._components]  # type: ignore
        return self.new(*new_components)

    """
    Note: There are a few challenges here.
    - How to align the types with int/float/Decimal/Fraction on the return type.
    - How to deal with floating point errors introduced by taking the sqrt.
    """

    def length(self: Vector[NumericType]) -> NumericTypeAlias:
        """Calculates the length of the vector."""
        sq_comps_sum: NumericTypeAlias = reduce(
            lambda a, b: a + b**2, self._components, cast(NumericType, 0)
        )
        return box_numeric_value(math.sqrt(sq_comps_sum), self.i)

    @enforce_vector_size
    def project_onto(self, b: Vector) -> Vector:
        """Create a new vector by projecting this vector onto vector B.
        See: https://en.wikipedia.org/wiki/Vector_projection

        The new vector C is the same direction as vector B, but is the length
        of the shadow of this vector "projected" onto vector B.
        C = dot(A, B)/squared(length(B)) * B
        """
        projected_distance: float = self.dot(b) / b.dot(b)
        return b.scale(projected_distance)

    @enforce_vector_type
    @enforce_vector_size
    def __mul__(self, other: Vector[NumericType]) -> NumericType:
        """Calculates the dot product between this vector and vector B."""
        return reduce(add, starmap(mul, zip(self, other)), cast(NumericType, 0))

    @enforce_vector_size
    def __sub__(self, other: Vector) -> Vector:
        """Enables using the - operator for vector subtraction."""
        # Expands to ai - bi, aj - bj, ... an - bn
        return self.new(*list(starmap(sub, zip(self, other))))

    @enforce_vector_size
    def __add__(self, other: Vector) -> Vector:
        """Enables using the + operator for vector addition."""
        return self.new(*list(starmap(add, zip(self, other))))

    def to_tuple(self) -> Tuple[NumericType, ...]:
        """Creates a tuple from the vector."""
        return tuple(self._components)

    def __hash__(self) -> int:
        """Return the hash value of the vector."""
        return hash(self.to_tuple())

    @enforce_vector_size
    def __eq__(self, other: Vector) -> bool:
        """
        Vector equality test. Supports comparing two vectors of the same dimension with
        a precision of 1e-7.
        """
        for index in range(len(self)):
            if not math.isclose(self[index], other[index], abs_tol=1e-7):
                return False
        return True

    def __iter__(self):
        return iter(self._components)

    def __getitem__(self, lookup: int) -> NumericType:
        """
        Enables using vector[index] to access the vector components.
        """
        return self._components[lookup]

    # Aliases
    dot = __mul__
