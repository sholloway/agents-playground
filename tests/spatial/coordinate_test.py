import pytest
from agents_playground.spatial.coordinate import Coordinate, CoordinateError


class TestCoordinate:
    def test_multiply(self) -> None:
        # Multiply on one dimension.
        assert Coordinate(2).multiply(Coordinate(4))[0] == 8

        # Multiply on three dimensions.
        c = Coordinate(1, 2, 3) * Coordinate(3, 4, 5)
        assert c[0] == 3
        assert c[1] == 8
        assert c[2] == 15

    def test_multiply_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(1, 2, 3).multiply(Coordinate(1))

    def test_add(self) -> None:
        # Add on one dimension.
        assert Coordinate(7).add(Coordinate(2))[0] == 9

        # Add on three dimensions.
        c: Coordinate = Coordinate(1, 2, 3) + Coordinate(3, 4, 5)
        assert c[0] == 4
        assert c[1] == 6
        assert c[2] == 8

    def test_add_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(1, 2, 3) + Coordinate(1)  # type: ignore

    def test_subtract(self) -> None:
        # Subtract on one dimension.
        assert Coordinate(100).subtract(Coordinate(90))[0] == 10

        # Subtract in three dimensions.
        a = Coordinate(1, 7, 10)
        b = Coordinate(3, 4, 5)
        c: Coordinate = a - b
        assert c[0] == -2
        assert c[1] == 3
        assert c[2] == 5

    def test_subtract_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(1, 2, 3) - Coordinate(1)  # type: ignore

    def test_shift(self) -> None:
        a = Coordinate(1, 2, 3)
        b = Coordinate(3, 4, 5)
        c: Coordinate = a.shift(b)
        assert c[0] == 4
        assert c[1] == 6
        assert c[2] == 8

    def test_to_tuple(self) -> None:
        assert Coordinate(17).to_tuple() == (17,)
        assert Coordinate(17, 23, 1102).to_tuple() == (17, 23, 1102)

    def test_find_manhattan_distance(self) -> None:
        # In one dimensions
        assert Coordinate(12).find_manhattan_distance(Coordinate(4)) == 8

        # In two dimensions
        assert Coordinate(1, 1).find_manhattan_distance(Coordinate(4, 5)) == 7

        # In three dimensions
        a = Coordinate(12, 2, 7)
        b = Coordinate(93, 104, 14)

        distance = a.find_manhattan_distance(b)
        assert a.find_manhattan_distance(b) == b.find_manhattan_distance(a)
        assert distance == 190

    def test_euclidean_distance(self) -> None:
        # In one dimensions
        assert Coordinate(12).find_euclidean_distance(Coordinate(4)) == 8

        # In two dimensions
        assert Coordinate(1, 1).find_euclidean_distance(Coordinate(4, 5)) == 5

        # In three dimensions
        assert (
            Coordinate(14, 7, 1).find_euclidean_distance(Coordinate(33, 2, 9))
            == 21.213203435596427
        )
