from decimal import Decimal
from fractions import Fraction
from typing import cast
from agents_playground.core.types import NumericType
from agents_playground.spatial.coordinate import d, f
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.matrix.matrix4x4 import m4
from agents_playground.spatial.transformation import Transformation
from agents_playground.spatial.vector.vector import Vector


class Translation(Transformation[NumericType]):
    def __init__(self) -> None:
        super().__init__()

    # fmt: off
    """
    Convenience class for constructing a 4x4 translation matrix
    of the form:
    T = | 1, 0, 0, X | 
        | 0, 1, 0, Y |
        | 0, 0, 1, Z | 
        | 0, 0, 0, 1 | 
    """
    # fmt: on

    def _build_matrix(self, x, y, z, one, zero) -> Matrix:
        # fmt: off
        return m4(
            one, zero, zero, x, 
            zero, one, zero, y, 
            zero, zero, one, z, 
            zero, zero, zero, one
        )
        # fmt: on

    def build_with_ints(self, *args) -> Matrix[int]:
        """
        Builds a 4x4 translation matrix with only integers.
        """
        return self._build_matrix(int(args[0]), int(args[1]), int(args[2]), 1, 0)

    def build_with_floats(self, *args) -> Matrix[float]:
        """
        Builds a 4x4 translation matrix with only floats.
        """
        return self._build_matrix(
            float(args[0]), float(args[1]), float(args[2]), 1.0, 0.0
        )

    def build_with_fractions(self, *args) -> Matrix[Fraction]:
        """
        Builds a 4x4 translation matrix with only fractions.
        """
        x = cast(Fraction, args[0]) if isinstance(args[0], Fraction) else f(args[0])
        y = cast(Fraction, args[1]) if isinstance(args[1], Fraction) else f(args[1])
        z = cast(Fraction, args[2]) if isinstance(args[2], Fraction) else f(args[2])

        return self._build_matrix(x, y, z, f(1), f(0))

    def build_with_decimals(self, *args) -> Matrix[Decimal]:
        """
        Builds a 4x4 translation matrix with only decimals.
        """
        x = cast(Decimal, args[0]) if isinstance(args[0], Decimal) else d(args[0])
        y = cast(Decimal, args[1]) if isinstance(args[1], Decimal) else d(args[1])
        z = cast(Decimal, args[2]) if isinstance(args[2], Decimal) else d(args[2])

        return self._build_matrix(x, y, z, d(1), d(0))
