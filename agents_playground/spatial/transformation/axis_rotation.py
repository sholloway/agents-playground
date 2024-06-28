from abc import ABC, abstractmethod
from decimal import Decimal
from fractions import Fraction
from math import cos, radians, sin
from typing import cast
from agents_playground.core.types import NumericType
from agents_playground.spatial.coordinate import d, f
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.matrix.matrix4x4 import m4
from agents_playground.spatial.transformation import Transformation


class AxisRotation(Transformation, ABC):
    @abstractmethod
    def _build_matrix(self, c, s, one, zero) -> Matrix: ...

    def build_with_ints(self, *args) -> Matrix[int]:
        """
        Builds a 4x4 translation matrix with only integers.
        """
        raise TypeError(
            "Constructing a rotation matrix of integers doesn't make sense. (e.g. cos(45) < 0)"
        )

    def build_with_floats(self, *args) -> Matrix[float]:
        """
        Builds a 4x4 translation matrix with only floats.
        """
        rads = radians(args[0])
        c: float = cos(rads)
        s: float = sin(rads)
        return self._build_matrix(c, s, 1.0, 0.0)

    def build_with_fractions(self, *args) -> Matrix[Fraction]:
        """
        Builds a 4x4 translation matrix with only fractions.
        """
        rads = radians(args[0])
        c: Fraction = f(cos(rads))
        s: Fraction = f(sin(rads))
        one = f(1)
        zero = f(0)
        return self._build_matrix(c, s, one, zero)

    def build_with_decimals(self, *args) -> Matrix[Decimal]:
        """
        Builds a 4x4 translation matrix with only decimals.
        """
        rads = radians(args[0])
        c: Decimal = d(cos(rads))
        s: Decimal = d(sin(rads))
        one = d(1)
        zero = d(0)
        return self._build_matrix(c, s, one, zero)


class RotationAroundXAxis(AxisRotation):
    def __init__(self) -> None:
        super().__init__()

    # fmt: off
    """
    Convenience class for constructing a 4x4 rotation matrix
    of the form:
    T = | 1, 0,      0,       0 | 
        | 0, cos(θ), -sin(θ), 0 |
        | 0, sin(θ), cos(θ),  0 | 
        | 0, 0,      0,       1 | 
    """
    # fmt: on

    def _build_matrix(self, c, s, one, zero) -> Matrix:
        # fmt: off
        return m4(
            one, zero,  zero, zero,
            zero, c,    -s,   zero,
            zero, s,    c,    zero,
            zero, zero, zero, one
        )
        # fmt: on


class RotationAroundYAxis(AxisRotation):
    def __init__(self) -> None:
        super().__init__()

    # fmt: off
    """
    Convenience class for constructing a 4x4 rotation matrix
    of the form:
    T = | cos(θ),  0,  sin(θ),  0 | 
        | 0,       1,  0,       0 |
        | -sin(θ), 0,  cos(θ),  0 | 
        | 0,       0,  0,       1 | 
    """
    # fmt: on

    def _build_matrix(self, c, s, one, zero) -> Matrix:
        # fmt: off
        return m4(
            c, zero, s, zero,
            zero, one, zero, zero,
            -s, zero, c, zero,
            zero, zero, zero, one
        )
        # fmt: on


class RotationAroundZAxis(AxisRotation):
    def __init__(self) -> None:
        super().__init__()

    # fmt: off
    """
    Convenience class for constructing a 4x4 rotation matrix
    of the form:
    T = | cos(θ),  -sin(θ),  0,  0 | 
        | sin(θ),  cos(θ),   0,  0 |
        | 0,       0,        1,  0 | 
        | 0,       0,        0,  1 | 
    """
    # fmt: on

    def _build_matrix(self, c, s, one, zero) -> Matrix:
        # fmt: off
        return m4(
            c,     -s,   zero, zero,
            s,     c,    zero, zero,
            zero,  zero, one,  zero,
            zero,  zero, zero, one
        )
        # fmt: on
