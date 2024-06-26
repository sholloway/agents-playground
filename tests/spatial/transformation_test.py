import pytest

from math import cos, radians, sin

from agents_playground.spatial.matrix.matrix3x3 import m3
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4, m4
from agents_playground.spatial.vector import vector
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.matrix.transformation import (
    TransformationPipeline,
    rotate_around,
)


@pytest.fixture
def t() -> TransformationPipeline:
    """A test fixture that returns an empty transformation"""
    return TransformationPipeline()

class TestTransformation:
    def test_empty_transformation(self, t: TransformationPipeline) -> None:
        assert t.transform() == Matrix4x4.identity()

    def test_transformation(self, t: TransformationPipeline) -> None:
        # fmt: off
        i = m4(
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        )

        a = m4(
            5, 7,  9, 10, 
            2, 3,  3, 8, 
            8, 10, 2, 3, 
            3, 3,  4, 8
        )

        b = m4(
            3,  10, 12, 18, 
            12, 1,  4,  9, 
            9,  10, 12, 2, 
            3,  12, 4,  10
        )
        
        t.mul(i).mul(a).mul(b)

        # Multiply Identity * Matrix A * Matrix B
        transformation_matrix = t.transform()

        assert transformation_matrix == m4(
            210, 267, 236, 271,
            93,  149, 104, 149,
            171, 146, 172, 268,
            105, 169, 128, 169,
        )
        # fmt: on

    def test_translation(self, t: TransformationPipeline) -> None:
        t.translate(vector(4, 5, 6))
        assert t.transform() == m4(1, 0, 0, 4, 0, 1, 0, 5, 0, 0, 1, 6, 0, 0, 0, 1)

    def test_rotate_around_x_axis(self, t: TransformationPipeline) -> None:
        angle = 90  # In degrees.
        rads = radians(angle)
        c = cos(rads)
        s = sin(rads)

        t.rotate_around_x(angle)

        assert t.transform() == m4(1, 0, 0, 0, 0, c, -s, 0, 0, s, c, 0, 0, 0, 0, 1)

    def test_rotate_around_y_axis(self, t: TransformationPipeline) -> None:
        angle = 72  # In degrees.
        rads = radians(angle)
        c = cos(rads)
        s = sin(rads)

        t.rotate_around_y(angle)

        assert t.transform() == m4(c, 0, s, 0, 0, 1, 0, 0, -s, 0, c, 0, 0, 0, 0, 1)

    def test_rotate_around_z_axis(self, t: TransformationPipeline) -> None:
        angle = 19  # In degrees.
        rads = radians(angle)
        c = cos(rads)
        s = sin(rads)

        t.rotate_around_z(angle)

        assert t.transform() == m4(c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)

    def test_scale(self, t: TransformationPipeline) -> None:
        x_scale_factor = 1.2
        y_scale_factor = 1  # No scale
        z_scale_factor = 4  # 4x

        t.scale(vector(x_scale_factor, y_scale_factor, z_scale_factor))

        assert t.transform() == m4(
            x_scale_factor,
            0,
            0,
            0,
            0,
            y_scale_factor,
            0,
            0,
            0,
            0,
            z_scale_factor,
            0,
            0,
            0,
            0,
            1,
        )

    def test_rotate_around_vector_function(self) -> None:
        point_on_z_axis = (0, 0, 15)
        point_on_y_axis = rotate_around(
            point_to_rotate=point_on_z_axis,
            rotation_point=(0, 0, 0),  # Rotate around the origin.
            axis=vector(1, 0, 0),  # rotate around the x-axis.
            angle=-90,  # Rotate 90 degrees.
        )

        # assert point_on_y_axis == (0, 15, 0)
        assert point_on_y_axis[0] == pytest.approx(0)
        assert point_on_y_axis[1] == pytest.approx(15)
        assert point_on_y_axis[2] == pytest.approx(0)

        negative_point_on_z_axis = rotate_around(
            point_to_rotate=point_on_y_axis,
            rotation_point=(0, 0, 0),  # Rotate around the origin.
            axis=vector(1, 0, 0),  # rotate around the x-axis.
            angle=-90,
        )

        # assert negative_point_on_z_axis == (0, 0, -15)
        assert negative_point_on_z_axis[0] == pytest.approx(0)
        assert negative_point_on_z_axis[1] == pytest.approx(0)
        assert negative_point_on_z_axis[2] == pytest.approx(-15)

    def test_rotate_around_vector(self, t: TransformationPipeline) -> None:
        t.rotate_around(
            rotation_point=(0.0, 0.0, 0.0), # Rotate around the origin.
            axis=vector(1.0, 0.0, 0.0),  # rotate around the x-axis.
            angle=-90,  # Rotate 90 degrees.)
        )
        point_on_z_axis = vector(
            0.0, 0.0, 15.0, 1.0
        )  # Extend the 3d point to use homogenous coordinates (i.e. w = 1).
        point_on_y_axis = t.transform() * point_on_z_axis  # type: ignore
        assert point_on_y_axis == vector(0, 15, 0, 1)

        negative_point_on_z_axis = t.transform() * point_on_y_axis
        assert negative_point_on_z_axis == vector(0, 0, -15, 1)

        # Rotate to the negative y-axis.
        negative_point_on_y_axis = t.transform() * negative_point_on_z_axis
        assert negative_point_on_y_axis == vector(0, -15, 0, 1)

        # Rotate to the original position on the z-axis.
        assert t.transform() * negative_point_on_y_axis == point_on_z_axis


def rotate_around_old(angle, axis):
    """Places a rotation matrix on the transformation stack.

    Parameters:
      angle: An angle in degrees to rotate.
      axis: The vector to perform a left-handed rotation around.
    """
    axis = axis.unit()  # Enforce that the provided vector is normalized.
    x = axis.i
    y = axis.j
    z = axis.k
    rads = radians(angle)
    sine = sin(rads)
    cosine = cos(rads)

    a = cosine + (1.0 - cosine) * (x * x)
    b = (1.0 - cosine) * (x * y) - x * sine
    c = (1.0 - cosine) * (x * z) + y * sine

    e = (1.0 - cosine) * (x * y) + z * sine
    f = cosine + (1.0 - cosine) * (y * y)
    g = (1.0 - cosine) * (y * z) - x * sine

    h = (1.0 - cosine) * (x * z) - y * sine
    i = (1.0 - cosine) * (y * z) + x * sine
    j = cosine + (1.0 - cosine) * (z * z)

    return m4(a, b, c, 0, e, f, g, 0, h, i, j, 0, 0, 0, 0, 1)
