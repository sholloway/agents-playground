import pytest
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vector.vector3d import Vector3d


class TestVector3d:
    def test_scale_vector(self) -> None:
        v = Vector3d(1, 2, 3)
        vv = v.scale(3)
        assert vv.i == 3
        assert vv.j == 6
        assert vv.k == 9

    @pytest.mark.skip(reason="Not implemented yet")
    def test_rotate(self) -> None:
        assert False

    def test_unit(self) -> None:
        unit = Vector3d(7, -2, 17.3).unit()
        assert unit.i == pytest.approx(0.37294766)
        assert unit.j == pytest.approx(-0.10655647)
        assert unit.k == pytest.approx(0.92171349)

    def test_length(self) -> None:
        assert Vector3d(2, 2, 2).length() == pytest.approx(3.46410162)
        assert Vector3d(-2, 2, 2).length() == pytest.approx(3.46410162)
        assert Vector3d(2, -2, 2).length() == pytest.approx(3.46410162)
        assert Vector3d(2, 2, -2).length() == pytest.approx(3.46410162)
        assert Vector3d(-2, -2, -2).length() == pytest.approx(3.46410162)

    def test_right_hand_perp(self) -> None:
        with pytest.raises(NotImplementedError):
            Vector3d(1, 1, 1).right_hand_perp()

    def test_left_hand_perp(self) -> None:
        with pytest.raises(NotImplementedError):
            Vector3d(1, 1, 1).left_hand_perp()

    def test_dot_product(self) -> None:
        v1 = Vector3d(22, 14, 25)
        v2 = Vector3d(17, 0, -17)
        dot = v1.dot(v2)
        assert dot == -51
        assert dot == v2.dot(v1)

    def test_cross_product(self) -> None:
        v1 = Vector3d(1, 0, 0)
        v2 = Vector3d(0, 1, 0)
        assert v1.cross(v2) == Vector3d(0, 0, 1)

    def test_project_onto(self) -> None:
        a = Vector3d(1, 2, 3)
        b = Vector3d(4, 5, 6)
        c = a.project_onto(b)
        assert c == Vector3d(1.66233768, 2.0779221, 2.49350652)