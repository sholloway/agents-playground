
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

from agents_playground.core.types import NumericType, NumericTypeAlias
from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.spatial.coordinate import Coordinate, d, f
from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4, m4
from agents_playground.spatial.transformation.axis_rotation import RotationAroundXAxis, RotationAroundYAxis, RotationAroundZAxis
from agents_playground.spatial.transformation.scale import Scale
from agents_playground.spatial.transformation.translation import Translation
from agents_playground.spatial.transformation.vector_rotation import VectorRotation
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
        self._rotate_around_x_axis = RotationAroundXAxis()
        self._rotate_around_y_axis = RotationAroundYAxis()
        self._rotate_around_z_axis = RotationAroundZAxis()
        self._rotate_at_point_around_vector = VectorRotation()

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

    def rotate_around_x(self, match_type: NumericTypeAlias, angle: Degrees) -> Self:
        """Places a rotation matrix on the transformation stack.

        Parameters:
          angle: An angle in degrees to rotate around the x-axis.
        """
        return self.mul(self._rotate_around_x_axis.build(match_type, angle))

    def rotate_around_y(self, match_type: NumericTypeAlias, angle: Degrees) -> Self:
        """Places a rotation matrix on the transformation stack.

        Parameters:
          angle: An angle in degrees to rotate around the y-axis.
        """
        return self.mul(self._rotate_around_y_axis.build(match_type, angle))

    def rotate_around_z(self, match_type: NumericTypeAlias, angle: Degrees) -> Self:
        """Places a rotation matrix on the transformation stack.

        Parameters:
          angle: An angle in degrees to rotate around the z-axis.
        """
        return self.mul(self._rotate_around_z_axis.build(match_type, angle))

    def rotate_around(
        self, rotation_point: Coordinate, axis: Vector, angle: Degrees
    ) -> Self:
        """Places a rotation matrix on the transformation stack.

        Parameters:
          rotation_point: The origin of the vector to rotate around.
          angle: An angle in degrees to rotate.
          axis: The vector to perform a left-handed rotation around.
          angle: The rotation amount specified in degrees.
        """
        return self.mul(self._rotate_at_point_around_vector.build(1.0, rotation_point, axis, angle))

    def scale(self, v: Vector) -> Self:
        """Places a scale matrix on the transformation stack.

        Parameters:
          v: A vector to scale (i.e. stretch or shrink) an item along.
        """
        return self.mul(self._scale.build(v.i, *v))