from fractions import Fraction
import math
from math import radians

from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vector.vector2d import Vector2d
from agents_playground.spatial.vertex import Vertex2d


class TestVector2dWithFloats:
    def test_from_vertices(self) -> None:
        v: Vector = Vector2d.from_vertices(Vertex2d(1, 1), Vertex2d(4, 2))
        assert v.i == -3
        assert v.j == -1

    def test_from_points(self) -> None:
        v: Vector = Vector2d.from_points(Coordinate(1, 2), Coordinate(3, 7))
        assert v.i == 2
        assert v.j == 5

    def test_scale_vector(self) -> None:
        v = Vector2d(4, 1)
        vv = v.scale(3)
        assert vv.i == 12
        assert vv.j == 3

    def test_vector_to_point(self) -> None:
        point = Vector2d(4, -2).to_point(vector_origin=Coordinate(7, 2))
        assert point[0] == 11
        assert point[1] == 0

    def test_vector_to_vertex(self) -> None:
        point = Vector2d(4, -2).to_vertex(vector_origin=Vertex2d(7, 2))
        assert point.coordinates[0] == 11
        assert point.coordinates[1] == 0

    def test_rotate(self) -> None:
        rotate_by = radians(90)
        east = Vector2d(1, 0)
        north = east.rotate(rotate_by)
        west = north.rotate(rotate_by)
        south = west.rotate(rotate_by)

        assert north == Vector2d(0, 1)
        assert west == Vector2d(-1, 0)
        assert south == Vector2d(0, -1)
        assert south.rotate(rotate_by) == east

    def test_length(self) -> None:
        assert Vector2d(2, 2).length() == 2.82842712
        assert Vector2d(2, -2).length() == 2.82842712
        assert Vector2d(-2, 2).length() == 2.82842712
        assert Vector2d(-2, -2).length() == 2.82842712

    def test_unit(self) -> None:
        u = Vector2d(2, -8).unit()
        assert u.i == 0.24253563
        assert u.j == -0.9701425
        assert u.length() == 1

    def test_right_hand_perp(self) -> None:
        i = 7.2
        j = -3.1
        v = Vector2d(i, j)
        rp = v.right_hand_perp()
        assert rp == Vector2d(j, -i).unit()

    def test_left_hand_perp(self) -> None:
        i = 7.2
        j = -3.1
        v = Vector2d(i, j)
        lp = v.left_hand_perp()
        assert lp == Vector2d(-j, i).unit()

    def test_project_onto(self) -> None:
        v = Vector2d(8, 2)
        o = Vector2d(17.2, 9.32)
        p = v.project_onto(o)
        assert p.i == 7.02197843
        assert p.j == 3.8049325

    def test_dot_product(self) -> None:
        # The angle between to vectors can be found with the dot product.
        # cos(theta) = (a dot b)/(len(a) * len(b))
        x_axis = Vector2d(1, 0)
        y_axis = Vector2d(0, 1)
        assert x_axis.dot(y_axis) / (x_axis.length() * y_axis.length()) == round(
            math.cos(radians(90)), 6
        )

    def test_cross_product(self) -> None:
        # The cross product between two vectors results in a vector that is perpendicular to the other two.
        # In 2D it is the right-handed perpendicular value of vector B
        x_axis = Vector2d(1, 0)
        y_axis = Vector2d(0, 1)
        assert x_axis.cross(y_axis) == y_axis.right_hand_perp()

        # The cross product can also be used to find the angle between two vectors.
        # | u X v | = |u|*|v|*sin(θ)
        # θ = arc_sign [ |u X v| / (|u| |v|) ]
        assert x_axis.cross(
            y_axis
        ).length() == x_axis.length() * y_axis.length() * math.sin(radians(90))

    def test_angle_direction(self) -> None:
        """Find the angle between two vectors joined at their tails."""
        # Quadrant I
        x_axis = Vector2d(1, 0)
        y_axis = Vector2d(0, 1)
        dot = x_axis.dot(y_axis)
        assert x_axis.dot(y_axis) == 0
        det = x_axis.i * y_axis.j - x_axis.j * y_axis.i
        assert det == 1
        assert math.atan2(det, dot) == radians(90)

        # Quadrant II
        x_axis = Vector2d(-1, 0)
        y_axis = Vector2d(0, 1)
        dot = x_axis.dot(y_axis)
        assert dot == 0
        det = x_axis.i * y_axis.j - x_axis.j * y_axis.i
        assert det == -1
        assert math.atan2(det, dot) == -radians(90)

        # Quadrant III
        x_axis = Vector2d(-1, 0)
        y_axis = Vector2d(0, -1)
        dot = x_axis.dot(y_axis)
        assert dot == 0
        det = x_axis.i * y_axis.j - x_axis.j * y_axis.i
        assert det == 1
        assert math.atan2(det, dot) == radians(90)

        # Quadrant IV
        x_axis = Vector2d(1, 0)
        y_axis = Vector2d(0, -1)
        dot = x_axis.dot(y_axis)
        assert dot == 0
        det = x_axis.i * y_axis.j - x_axis.j * y_axis.i
        assert det == -1
        assert math.atan2(det, dot) == -radians(90)

def f(numerator: int, denominator: int=1) -> Fraction:
    return Fraction(numerator, denominator)

class TestVector2dWithFractions:
    def test_from_points(self) -> None:
        v: Vector = Vector2d.from_points(Coordinate(f(1), f(2)), Coordinate(f(3), f(7)))
        assert v.i == 2
        assert v.j == 5
        assert isinstance(v.i, Fraction)
        assert isinstance(v.j, Fraction)

    def test_scale_vector(self) -> None:
        v = Vector2d(f(4), f(1))
        vv = v.scale(3)
        assert vv.i == 12
        assert vv.j == 3

    def test_vector_to_point(self) -> None:
        assert False

    def test_vector_to_vertex(self) -> None:
        assert False

    def test_rotate(self) -> None:
        assert False

    def test_length(self) -> None:
        assert False

    def test_unit(self) -> None:
        assert False

    def test_right_hand_perp(self) -> None:
        assert False

    def test_left_hand_perp(self) -> None:
        assert False

    def test_project_onto(self) -> None:
        assert False

    def test_dot_product(self) -> None:
        # The angle between to vectors can be found with the dot product.
        # cos(theta) = (a dot b)/(len(a) * len(b))
        assert False

    def test_cross_product(self) -> None:
        # The cross product between two vectors results in a vector that is perpendicular to the other two.
        # In 2D it is the right-handed perpendicular value of vector B
        assert False

    def test_angle_direction(self) -> None:
        """Find the angle between two vectors joined at their tails."""
        assert False