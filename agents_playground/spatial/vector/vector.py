from __future__ import annotations
from abc import ABC, abstractmethod
from itertools import starmap
import math
from functools import reduce, wraps
from operator import add, mul, sub
from typing import Generic, Tuple, TypeVar, cast

from deprecated import deprecated

from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.types import Radians
from agents_playground.spatial.vertex import Vertex, Vertex2d, Vertex3d

VECTOR_ROUNDING_PRECISION: int = 8
VectorType = TypeVar("VectorType", int, float)

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
            error_msg = f"Cannot perform this operation on vectors that are of different sizes."
            raise VectorError(error_msg)

    return _guard

class Vector(Generic[VectorType], ABC):
    """
    Represents the contract for a vector.
    """
    def __init__(self, *components: VectorType) -> None:
        self._components = list(*components)

    @abstractmethod
    def new(self, *args: VectorType) -> Vector[VectorType]:
        """Create a new vector with the same shape but with the provided data."""

    @abstractmethod
    def cross(self, b: Vector) -> Vector:
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
    def i(self) -> VectorType:
        """Returns the I component of the vector."""
        return self._components[0]

    @i.setter
    def i(self, other: VectorType) -> None:
        """Sets the I component of the vector."""
        self._components[0] = other

    @property
    def j(self) -> VectorType:
        """Returns the J component of the vector."""
        return self._components[1]

    @j.setter
    def j(self, other: VectorType) -> None:
        """Sets the J component of the vector."""
        self._components[1] = other

    @property
    def k(self) -> VectorType:
        """Returns the K component of the vector."""
        if len(self._components) > 2:
            return self._components[2] 
        return 0 #type: ignore
    
    @k.setter
    def k(self, other: VectorType) -> None:
        """Sets the K component of the vector."""
        if len(self._components) > 2:
            self._components[2] = other
        else:
            raise NotImplemented()

    @property
    def w(self) -> VectorType:
        """Returns the W component of the vector."""
        if len(self._components) > 3:
            return self._components[3] 
        return 0 #type: ignore

    @w.setter
    def w(self, other: VectorType) -> None:
        """Sets the W component of the vector."""
        if len(self._components) > 3:
            self._components[3] = other
        else:
            raise NotImplemented()

    def __len__(self) -> int:
        return len(self._components)
    
    def __repr__(self) -> str:
        t = self.to_tuple()
        return f"Vector{len(t)}d({','.join(map(str, t))})"
        
    def scale(self, scalar: VectorType) -> Vector[VectorType]:
        """Scale a vector by a scalar"""
        new_components = [ 
            round(component * scalar, VECTOR_ROUNDING_PRECISION)
            for component in self._components 
        ]
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
                new_components.append(component + vector_origin[index]) # type: ignore
            return Coordinate(*new_components)
        else:
            error_msg = (
                "Cannot offset a vector to a coordinate that has a different dimension.",
                f"Vector has {len(self)} components.",
                f"The coordinate has {len(vector_origin)} components."
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
                new_components.append(component + vector_origin.coordinates[index]) # type: ignore

            if isinstance(vector_origin, Vertex2d):
                return Vertex2d(new_components[0], new_components[1])
            elif isinstance(vector_origin, Vertex3d):
                return Vertex3d(new_components[0], new_components[1], new_components[2])
            else:
                error_msg = "Unsupported vertex type."
                raise VectorError(error_msg)
        else:
            error_msg = (
                "Cannot offset a vector to a coordinate that has a different dimension.",
                f"Vector has {len(self)} components.",
                f"The coordinate has {len(vector_origin)} components."
            )
            raise VectorError(error_msg)

    def unit(self) -> Vector[VectorType]:
        """Returns the unit vector as a new vector."""
        length = self.length()
        return self.new(
            *[
                round(c/length, VECTOR_ROUNDING_PRECISION) 
                for c in self._components
            ]
        )

    def length(self) -> float:
        """Calculates the length of the vector."""
        sq_comps_sum = reduce(lambda a,b: a + b**2, self._components, 0)
        return round(math.sqrt(sq_comps_sum), VECTOR_ROUNDING_PRECISION)

    def project_onto(self, b: Vector) -> Vector:
        """Create a new vector by projecting this vector onto vector B.
        See: https://en.wikipedia.org/wiki/Vector_projection

        The new vector C is the same direction as vector B, but is the length
        of the shadow of this vector "projected" onto vector B.
        C = dot(A, B)/squared(length(B)) * B
        """
        projected_distance: float = round(
            self.dot(b) / b.dot(b), VECTOR_ROUNDING_PRECISION
        )
        return b.scale(projected_distance)

    
    def dot(self, other: Vector) -> float:
        """Calculates the dot product between this vector and vector B."""
        return reduce(add, starmap(mul, zip(self, other)), 0)

    def __mul__(self, other: Vector) -> float:
        """Enables using the * operator for the dot product."""
        return self.dot(other)

    def __sub__(self, other: Vector) -> Vector:
        """Enables using the - operator for vector subtraction."""
        # Expands to ai - bi, aj - bj, ... an - bn
        return self.new(*list(starmap(sub, zip(self,other))))

    def __add__(self, other: Vector) -> Vector:
        """Enables using the + operator for vector addition."""
        return self.new(*list(starmap(add, zip(self,other))))

    def to_tuple(self) -> Tuple[float, ...]:
        """Creates a tuple from the vector."""
        return tuple(self._components)

    def __hash__(self) -> int:
        """Return the hash value of the vector."""
        return hash(self.to_tuple())
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector):
            return self.to_tuple().__eq__(other.to_tuple())
        else:
            return self.to_tuple().__eq__(other)

    def __iter__(self):
        return iter(self._components)