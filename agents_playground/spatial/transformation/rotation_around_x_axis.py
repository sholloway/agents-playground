from decimal import Decimal
from fractions import Fraction
from math import cos, radians, sin
from typing import cast
from agents_playground.core.types import NumericType
from agents_playground.spatial.coordinate import d, f
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.matrix.matrix4x4 import m4
from agents_playground.spatial.transformation import Transformation
from agents_playground.spatial.vector.vector import Vector

class RotationAroundXAxis(Transformation[NumericType]):
    # fmt: off
    """
    Convenience class for constructing a 4x4 rotation matrix
    of the form:
    T = | 1, 0,      0,       0 | 
        | 0, cos(θ), -sin(θ), Y |
        | 0, sin(θ), v,       0 | 
        | 0, 0,      0,       1 | 
    """
    # fmt: on
    def build_with_ints(self, v: Vector[NumericType]) -> Matrix[int]:
        """
        Builds a 4x4 translation matrix with only integers.
        """
        # fmt: off
        return m4(
            1, 0, 0, int(v.i), 
            0, 1, 0, int(v.j), 
            0, 0, 1, int(v.k), 
            0, 0, 0, 1
        )
        # fmt: on
    
    def build_with_floats(self, v: Vector[NumericType]) -> Matrix[float]:
        """
        Builds a 4x4 translation matrix with only floats.
        """
        # fmt: off
        return m4(
            1.0, 0.0, 0.0, float(v.i), 
            0.0, 1.0, 0.0, float(v.j), 
            0.0, 0.0, 1.0, float(v.k), 
            0.0, 0.0, 0.0, 1.0
        )
        # fmt: on
    
    def build_with_fractions(self, v: Vector[NumericType]) -> Matrix[Fraction]:
        """
        Builds a 4x4 translation matrix with only fractions.
        """
        one = f(1)
        zero = f(0)
        
        x = cast(Fraction, v.i) if isinstance(v.i, Fraction) else f(v.i)
        y = cast(Fraction, v.j) if isinstance(v.j, Fraction) else f(v.j)
        z = cast(Fraction, v.k) if isinstance(v.k, Fraction) else f(v.k)

        # fmt: off
        return m4(
            one, zero, zero, x, 
            zero, one, zero, y, 
            zero, zero, one, z, 
            zero, zero, zero, one
        )
        # fmt: on

    def build_with_decimals(self, v: Vector[NumericType]) -> Matrix[Decimal]:
        """
        Builds a 4x4 translation matrix with only decimals.
        """
        one = d(1)
        zero = d(0)

        x = cast(Decimal, v.i) if isinstance(v.i, Decimal) else d(v.i)
        y = cast(Decimal, v.j) if isinstance(v.j, Decimal) else d(v.j)
        z = cast(Decimal, v.k) if isinstance(v.k, Decimal) else d(v.k)

        # fmt: off
        return m4(
            one, zero, zero, x, 
            zero, one, zero, y, 
            zero, zero, one, z, 
            zero, zero, zero, one
        )
        # fmt: on