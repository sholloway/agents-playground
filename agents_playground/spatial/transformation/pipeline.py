
from array import array as create_array
from array import ArrayType
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from operator import mul
from functools import reduce
from math import cos, radians, sin
from typing import Generic, Self, assert_never, cast

import wgpu

from agents_playground.core.types import NumericType
from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.spatial.coordinate import d, f
from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4, m4
from agents_playground.spatial.transformation.scale import Scale
from agents_playground.spatial.transformation.translation import Translation
from agents_playground.spatial.types import Degrees
from agents_playground.spatial.vector import vector
from agents_playground.spatial.vector.vector import Vector



class TransformationPipeline:
    """Convenance class for working with Affine Transformations.

    A transformation is a set of affine transformations that are applied
    to a vertex or vector in the order that they're added.

    Example:
    To construct a transformation matrix of T = A*B*C:
    t = TransformationPipeline()
    t.mul(A).mul(B).mul(c)
    transformation_matrix = t.transform()
    """

    def __init__(self) -> None:
        self._stack: list[Matrix] = []
        self._has_changed: bool = False
        self._cached_transform: Maybe[Matrix] = Nothing()
        self._translation = Translation() 
        self._scale = Scale()

    def transform(self) -> Matrix:
        # fmt: off
        """Returns the combined transformation matrix.
        Multiplies all matrices from left to right with the first item added
        considered the left most item.

        In the text Real-time Rendering by Akenine-Möller, Haines, Hoffman
        this operation is referred to as transformation concatenation.

        Keep in mind that the order of applying transformations matter.

        To apply the classic Translate/Rotate/Scale pattern build a
        transformation pipeline as follows.
        t = TransformationPipeline()
            t.translate(destination_vector) \
            .rotate_around() \
            .scale_by()
            transformation: Matrix = t.transform()
        """
        # fmt: on
        if len(self._stack) < 1:
            return Matrix4x4.identity()

        if not self._cached_transform.is_something() or self._has_changed:
            self._cached_transform = Something(reduce(mul, self._stack))
            self._has_changed = False
        
        return self._cached_transform.unwrap_or_throw('The cached transform was not set.')

    def clear(self) -> Self:
        """Resets the transformation stack to be empty."""
        self._stack.clear()
        self._has_changed = False
        self._cached_transform = Nothing()
        return self

    def mul(self, m: Matrix) -> Self:
        """Places a matrix on the transformation stack."""
        self._stack.append(m)
        return self

    def identity(self) -> Self:
        """Places the identity matrix on the transformation stack"""
        return self.mul(Matrix4x4.identity())

    def translate(self, v: Vector) -> Self:
        """Places a translation matrix on the transformation stack.

        Parameters:
          v: A vector to translate (i.e. move) an item along.
        """
        return self.mul(self._translation.build(v.i, *v))

    def rotate_around_x(self, angle: Degrees) -> Self:
        """Places a rotation matrix on the transformation stack.

        Parameters:
          angle: An angle in degrees to rotate around the x-axis.
        """
        rads = radians(angle)
        c = cos(rads)
        s = sin(rads)
        return self.mul(
            m4(
                1, 0, 0, 0, 
                0, c, -s, 0, 
                0, s, c, 0, 
                0, 0, 0, 1))

    def rotate_around_y(self, angle: Degrees) -> Self:
        """Places a rotation matrix on the transformation stack.

        Parameters:
          angle: An angle in degrees to rotate around the y-axis.
        """
        rads = radians(angle)
        c = cos(rads)
        s = sin(rads)
        return self.mul(m4(c, 0, s, 0, 0, 1, 0, 0, -s, 0, c, 0, 0, 0, 0, 1))

    def rotate_around_z(self, angle: Degrees) -> Self:
        """Places a rotation matrix on the transformation stack.

        Parameters:
          angle: An angle in degrees to rotate around the z-axis.
        """
        rads = radians(angle)
        c = cos(rads)
        s = sin(rads)
        return self.mul(m4(c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))

    def rotate_around(
        self, rotation_point: tuple[float, ...], axis: Vector, angle: Degrees
    ) -> Self:
        """Places a rotation matrix on the transformation stack.

        Parameters:
          rotation_point: The origin of the vector to rotate around.
          angle: An angle in degrees to rotate.
          axis: The vector to perform a left-handed rotation around.
          angle: The rotation amount specified in degrees.
        """
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
        return self.mul(
            m4(
                m00, m01, m02, m03, 
                m10, m11, m12, m13, 
                m20, m21, m22, m23, 
                0.0, 0.0, 0.0, 1.0
            )
        )
        # fmt: on

    def scale(self, v: Vector) -> Self:
        """Places a scale matrix on the transformation stack.

        Parameters:
          v: A vector to scale (i.e. stretch or shrink) an item along.
        """
        return self.mul(self._scale.build(v.i, *v))