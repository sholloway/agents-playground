import pytest

from fractions import Fraction

from agents_playground.spatial.coordinate import Coordinate, CoordinateError

def f(numerator: int, denominator: int=1) -> Fraction:
    return Fraction(numerator, denominator)

class TestCoordinateWithFloats:
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

class TestCoordinateWithFractions:
    def test_multiply(self) -> None:
        # Multiply on one dimension.
        assert Coordinate(f(2)).multiply(Coordinate(f(4)))[0] == f(8)

        # Multiply on three dimensions.
        c = Coordinate(f(1), f(2), f(3)) * Coordinate(f(3), f(4), f(5))
        assert c[0] == f(3)
        assert c[1] == f(8)
        assert c[2] == f(15)

    def test_multiplying_returns_fractions(self) -> None:
        result = Coordinate(f(2)).multiply(Coordinate(f(4)))
        assert isinstance(result[0], Fraction)

    def test_enforces_type(self) -> None:
        with pytest.raises(CoordinateError) as ce:
            # Try to mix fractions and floats
            Coordinate(f(1,2)).multiply(Coordinate(4.13)) # type: ignore
        assert str(ce.value) == "Cannot mix coordinates of different types."

    def test_multiply_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(f(1), f(2), f(3)).multiply(Coordinate(f(1)))

    def test_add(self) -> None:
        # Add on one dimension.
        assert Coordinate(f(1, 4)).add(Coordinate(f(2, 4)))[0] == f(3, 4)

        # Add on three dimensions.
        c: Coordinate = Coordinate(f(1), f(2), f(3)) + Coordinate(f(3), f(4), f(5))
        assert c[0] == 4
        assert c[1] == 6
        assert c[2] == 8

    def test_add_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(f(1), f(2), f(3)) + Coordinate(f(1))  # type: ignore

    def test_subtract(self) -> None:
        # Subtract on one dimension.
        assert Coordinate(f(100)).subtract(Coordinate(f(90)))[0] == 10

        # Subtract in three dimensions.
        a = Coordinate(f(1), f(7), f(10))
        b = Coordinate(f(3), f(4), f(5))
        c: Coordinate = a - b
        assert c[0] == -2
        assert c[1] == 3
        assert c[2] == 5

    def test_subtract_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(f(1), f(2), f(3)) - Coordinate(f(1))  # type: ignore

    def test_shift(self) -> None:
        a = Coordinate(f(1), f(2), f(3))
        b = Coordinate(f(3), f(4), f(5))
        c: Coordinate = a.shift(b)
        assert c[0] == 4
        assert c[1] == 6
        assert c[2] == 8

    def test_to_tuple(self) -> None:
        assert Coordinate(f(17)).to_tuple() == (f(17),)
        assert Coordinate(f(1, 17), f(2, 3), f(11, 2)).to_tuple() == (f(1,17), f(2, 3), f(11, 2))

    def test_find_manhattan_distance(self) -> None:
        # In one dimensions
        assert Coordinate(f(12)).find_manhattan_distance(Coordinate(f(4))) == 8

        # In two dimensions
        assert Coordinate(f(1), f(1)).find_manhattan_distance(Coordinate(f(4), f(5))) == 7

        # In three dimensions
        a = Coordinate(f(12), f(2), f(7))
        b = Coordinate(f(93), f(104), f(14))

        distance = a.find_manhattan_distance(b)
        assert a.find_manhattan_distance(b) == b.find_manhattan_distance(a)
        assert distance == 190

    def test_euclidean_distance(self) -> None:
        # In one dimensions
        assert Coordinate(f(12)).find_euclidean_distance(Coordinate(f(4))) == 8

        # In two dimensions
        assert Coordinate(f(1), f(1)).find_euclidean_distance(Coordinate(f(4), f(5))) == 5

        # In three dimensions
        distance_in_3d = Coordinate(f(14), f(7), f(1)).find_euclidean_distance(Coordinate(f(33), f(2), f(9)))
        assert distance_in_3d, 21.213203435596427
        assert isinstance(distance_in_3d, Fraction)
        
