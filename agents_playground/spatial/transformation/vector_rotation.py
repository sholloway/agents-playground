from decimal import Decimal
from fractions import Fraction
from math import cos, radians, sin
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.matrix.matrix4x4 import m4
from agents_playground.spatial.transformation import Transformation
from agents_playground.spatial.types import Degrees
from agents_playground.spatial.vector.vector import Vector


class VectorRotation(Transformation):
    def __init__(self) -> None:
        super().__init__()

    def build_with_ints(self, *args) -> Matrix[int]:
        """
        Builds a 4x4 transformation matrix composed of integers.
        """
        raise NotImplementedError()

    def build_with_floats(self, *args) -> Matrix[float]:
        """
        Builds a 4x4 transformation matrix composed of floats.
        """
        rotation_point: Coordinate = args[0]
        axis: Vector = args[1]
        angle: Degrees = args[2]

        # Source: https://sites.google.com/site/glennmurray/Home/rotation-matrices-and-formulas

        # Establish aliases for the point to rotate around's components.
        a: float = rotation_point[0]
        b: float = rotation_point[1]
        c: float = rotation_point[2]

        # Ensure that the axis has a length of 1.
        axis_norm = axis.unit()

        # Establish aliases for the vector to rotate around's components.
        u = axis_norm.i
        v = axis_norm.j
        w = axis_norm.k

        # Calculate the trig functions.
        rads: float = radians(angle)
        cosine: float = cos(rads)
        one_minus_cosine: float = 1 - cosine
        sine: float = sin(rads)

        # Establish aliases for the various products used in the rotation equations.
        u_sq = u * u
        v_sq = v * v
        w_sq = w * w

        au = a * u
        av = a * v
        aw = a * w

        bu = b * u
        bv = b * v
        bw = b * w

        cu = c * u
        cv = c * v
        cw = c * w

        uv = u * v
        uw = u * w
        vw = v * w

        # Evaluate the components of the rotation transformation.
        m00 = u_sq + (v_sq + w_sq) * cosine
        m01 = uv * one_minus_cosine - w * sine
        m02 = uw * one_minus_cosine + v * sine
        m03 = (a * (v_sq + w_sq) - u * (bv + cw)) * one_minus_cosine + (bw - cv) * sine

        m10 = uv * one_minus_cosine + w * sine
        m11 = v_sq + (u_sq + w_sq) * cosine
        m12 = vw * one_minus_cosine - u * sine
        m13 = (b * (u_sq + w_sq) - v * (au + cw)) * one_minus_cosine + (cu - aw) * sine

        m20 = uw * one_minus_cosine - v * sine
        m21 = vw * one_minus_cosine + u * sine
        m22 = w_sq + (u_sq + v_sq) * cosine
        m23 = (c * (u_sq + v_sq) - w * (au + bv)) * one_minus_cosine + (av - bu) * sine

        # fmt: off
        return m4(
            m00, m01, m02, m03, 
            m10, m11, m12, m13, 
            m20, m21, m22, m23, 
            0.0, 0.0, 0.0, 1.0
        )
        # fmt: on

    def build_with_fractions(self, *args) -> Matrix[Fraction]:
        """
        Builds a 4x4 transformation matrix composed of fractions.
        """
        raise NotImplementedError()

    def build_with_decimals(self, *args) -> Matrix[Decimal]:
        """
        Builds a 4x4 transformation matrix composed of decimals.
        """
        raise NotImplementedError()
