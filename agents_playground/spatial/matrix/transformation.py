from array import array as create_array
from array import ArrayType
from dataclasses import dataclass
from operator import mul
from functools import reduce
from math import cos, radians, sin
from typing import Self

import wgpu

from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4, m4
from agents_playground.spatial.types import Degrees
from agents_playground.spatial.vector import vector
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


class TransformationPipeline:
    """Convenance class for working with Affine Transformations.

    A transformation is a set of affine transformations that are applied
    to a vertex or vector in the order that they're added.

    Example:
    To construct a transformation matrix of T = A*B*C:
    t = Transformation()
    t.mul(A).mul(B).mul(c)
    transformation_matrix = t.transform()
    """

    def __init__(self) -> None:
        self._stack: list[Matrix] = []
        self._has_changed: bool = False
        self._cached_transform: Maybe[Matrix] = Nothing()

    def transform(self) -> Matrix:
        """Returns the combined transformation matrix.
    Multiplies all matrices from left to right with the first item added
    considered the left most item.

    In the text Real-time Rendering by Akenine-Möller, Haines, Hoffman
    this operation is referred to as transformation concatenation.

    Keep in mind that the order of applying transformations matter.

    To apply the classic Translate/Rotate/Scale pattern build a
    transformation pipeline as follows.
    t = Transformation()
    t.translate(destination_vector) \
      .rotate_around() \
      .scale_by()
    transformation: Matrix = t.transform()
    """
        if len(self._stack) < 1:
            return Matrix4x4.identity()

        if not self._cached_transform.is_something() or self._has_changed:
            self._cached_transform = Something(reduce(mul, self._stack))
            self._has_changed = False
        return self._cached_transform.unwrap()

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
        return self.mul(m4(1, 0, 0, v.i, 0, 1, 0, v.j, 0, 0, 1, v.k, 0, 0, 0, 1))

    def rotate_around_x(self, angle: Degrees) -> Self:
        """Places a rotation matrix on the transformation stack.

        Parameters:
          angle: An angle in degrees to rotate around the x-axis.
        """
        rads = radians(angle)
        c = cos(rads)
        s = sin(rads)
        return self.mul(m4(1, 0, 0, 0, 0, c, -s, 0, 0, s, c, 0, 0, 0, 0, 1))

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

        return self.mul(
            m4(m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, 0, 0, 0, 1)
        )

    def scale(self, v: Vector) -> Self:
        """Places a scale matrix on the transformation stack.

        Parameters:
          v: A vector to scale (i.e. stretch or shrink) an item along.
        """
        return self.mul(m4(v.i, 0, 0, 0, 0, v.j, 0, 0, 0, 0, v.k, 0, 0, 0, 0, 1))


"""
I need Matrix -> Buffer.

There are a few steps.
0. Create the array that will fill the buffer.
model_world_transform_data = create_array('f', matrix.flatten(MatrixOrder.Row))

1. Create an empty buffer.
device: wgpu.GPUDevice
model_to_world_buffer: wgpu.GPUDevice = device.create_buffer(
  label = 'Model Transform Buffer',
  size = 4 * 16,
  usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST # type: ignore
)

2. Create the bind group for the buffer.
bind_group_layout: GPUBindGroupLayout
bind_group: wgpu.GPUBindGroup = device.create_bind_group(
  label   = 'Camera Bind Group',
  layout  = bind_group_layout,
  entries = [
    {
      'binding': 0,
      'resource': {
        'buffer': model_to_world_buffer,
        'offset': 0,
        'size': model_to_world_buffer.size
      }
    }
  ]
)

4. Write the data into the buffer and place it on the GPUQueue.
queue.write_buffer(model_to_world_buffer, 0, model_world_transform_data)
"""


@dataclass
class TransformationConfiguration:
    """
    A collection of vectors that are used to build a transformation pipeline.

    Attributes:
      translation: Three member list that specifies the distance along the three axes to move the item.
      rotation: Three member list of angles in degrees that specifies the amount to rotate around the axes.
      scale: Three member list of floats that specify the amount to scale along each axis.
      transformation_data: The transformation matrix resulting from multiplying T*R*S.
      transformation_buffer: The GPUBuffer to hold the transformation data.
    """

    # These attributes are intended to be loaded from Scene files.
    translation: list[float]
    rotation: list[float]
    scale: list[float]

    # These attributes are used by per frame processing.
    transformation_data: Maybe[ArrayType] = Nothing()
    transformation_buffer: Maybe[wgpu.GPUBuffer] = Nothing()

    def transform(self) -> None:
        """
        Creates a transformation pipeline to build a matrix from the various
        transformations and then stores it in the transformation_data.
        """
        tp = TransformationPipeline()
        if len(self.translation) == 3:
            tp.translate(vector(*self.translation))

        if len(self.rotation) == 3:
            self._create_rotation_transforms(tp)

        if len(self.scale) == 3:
            self._create_scale_transforms(tp)

        m = tp.transform()
        self.transformation_data = Something(
            create_array("f", m.flatten(MatrixOrder.Row))
        )

    def _create_rotation_transforms(self, tp: TransformationPipeline) -> None:
        if self.rotation[0] != 0:
            tp.rotate_around_x(self.rotation[0])

        if self.rotation[1] != 0:
            tp.rotate_around_y(self.rotation[1])

        if self.rotation[2] != 0:
            tp.rotate_around_z(self.rotation[2])

    def _create_scale_transforms(self, tp: TransformationPipeline) -> None:
        if self.scale[0] != 1 or self.scale[1] != 1 or self.scale[2] != 1:
            tp.scale(vector(*self.scale))
