from abc import ABC, abstractmethod
from decimal import Decimal
from fractions import Fraction
from math import cos, radians, sin
from typing import Generic, assert_never

from agents_playground.core.types import NumericType
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.types import Degrees
from agents_playground.spatial.vector.vector import Vector

def rotate_around(
    point_to_rotate: tuple[float, ...],
    rotation_point: tuple[float, ...],
    axis: Vector,
    angle: Degrees,
) -> tuple[float, ...]:
    """Convenance function to rotate a point around a vector.

    This function is equivalent to
    t = Transformation()
    t.rotate_around(rotation_point, axis, angle)
    new_location = t.transform() * point_to_rotate

    Parameters:
      point_to_rotate: The point that shall be rotated.
      rotation_point: The origin of the vector to rotate around.
      axis: The vector to rotate the point around.
      angle: The rotation amount specified in degrees.

    Returns:
    The new location of the point.
    """
    # Source: https://sites.google.com/site/glennmurray/Home/rotation-matrices-and-formulas
    # Establish aliases for the point to rotate's components.
    x = point_to_rotate[0]
    y = point_to_rotate[1]
    z = point_to_rotate[2]

    # Establish aliases for the point to rotate around's components.
    a = rotation_point[0]
    b = rotation_point[1]
    c = rotation_point[2]

    # Ensure that the axis has a length of 1.
    axis_norm = axis.unit()

    # Establish aliases for the vector to rotate around's components.
    u = axis_norm.i
    v = axis_norm.j
    w = axis_norm.k

    # Calculate the trig functions.
    rads = radians(angle)
    cosine = cos(rads)
    one_minus_cosine = 1 - cosine
    sine = sin(rads)

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

    ux = u * x
    uy = u * y
    uz = u * z

    vx = v * x
    vy = v * y
    vz = v * z

    wx = w * x
    wy = w * y
    wz = w * z

    # Evaluate the rotation equations.
    new_x = (
        (a * (v_sq + w_sq) - u * (bv + cw - ux - vy - wz)) * one_minus_cosine
        + x * cosine
        + (-cv + bw - wy + vz) * sine
    )
    new_y = (
        (b * (u_sq + w_sq) - v * (au + cw - ux - vy - wz)) * one_minus_cosine
        + y * cosine
        + (cu - aw + wx - uz) * sine
    )
    new_z = (
        (c * (u_sq + v_sq) - w * (au + bv - ux - vy - wz)) * one_minus_cosine
        + z * cosine
        + (-bu + av - vx + uy) * sine
    )
    return (new_x, new_y, new_z)

class Transformation(ABC, Generic[NumericType]):
    def build(self, match_type: NumericType, *args) -> Matrix[NumericType]:
        """
        Builds a 4x4 translation matrix with the same numeric type 
        provided.
        """
        transformation: Matrix
        
        match match_type:
            case int():
                transformation = self.build_with_ints(*args)
            case float():
                transformation = self.build_with_floats(*args)
            case Fraction():
                transformation = self.build_with_fractions(*args)
            case Decimal():
                transformation = self.build_with_decimals(*args)
            case _:
                assert_never(match_type)
        return transformation
    
    @abstractmethod
    def build_with_ints(self, *args) -> Matrix[int]:
        """
        Builds a 4x4 transformation matrix composed of integers.
        """

    @abstractmethod
    def build_with_floats(self, *args) -> Matrix[float]:
        """
        Builds a 4x4 transformation matrix composed of floats.
        """   

    @abstractmethod
    def build_with_fractions(self, *args) -> Matrix[Fraction]:
        """
        Builds a 4x4 transformation matrix composed of fractions.
        """

    @abstractmethod
    def build_with_decimals(self, *args) -> Matrix[Decimal]:
        """
        Builds a 4x4 transformation matrix composed of decimals.
        """

from . import *