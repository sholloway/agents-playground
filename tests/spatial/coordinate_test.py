import pytest

from decimal import Decimal
from fractions import Fraction

from agents_playground.core.types import NumericTypeError
from agents_playground.spatial.coordinate import Coordinate, CoordinateError, d, f

class TestCoordinate:
    def test_enforce_init_same_type_only(self) -> None:
        Coordinate(1, 2, 3) # ints are fine
        Coordinate(1.0, 2.0, 3.0) # floats are fine
        Coordinate(Fraction(1,2), Fraction(3/4)) # Fractions are fine.
        Coordinate(Decimal(1.04), Decimal(7.082), Decimal(999.142)) # Decimals are fine

        with pytest.raises(NumericTypeError) as error:
            Coordinate(2, 1.0) # Mix int and float
        assert str(error.value) == 'Cannot mix parameter types.'

    def test_multiply(self) -> None:
        # Multiply on one dimension.
        assert Coordinate(2).multiply(Coordinate(4))[0] == 8

        # Multiply on three dimensions.
        c = Coordinate(1, 2, 3) * Coordinate(3, 4, 5)
        assert c == Coordinate(3, 8, 15)
        

    def test_multiply_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(1, 2, 3).multiply(Coordinate(1))

    def test_add(self) -> None:
        # Add on one dimension.
        assert Coordinate(7).add(Coordinate(2))[0] == 9

        # Add on three dimensions.
        c: Coordinate = Coordinate(1, 2, 3) + Coordinate(3, 4, 5)
        assert c == Coordinate(4, 6, 8)

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
        assert c == Coordinate(-2, 3, 5)

    def test_subtract_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(1, 2, 3) - Coordinate(1)  # type: ignore

    def test_shift(self) -> None:
        a = Coordinate(1, 2, 3)
        b = Coordinate(3, 4, 5)
        c: Coordinate = a.shift(b)
        assert c == Coordinate(4, 6, 8)

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
        assert c == Coordinate(f(3), f(8), f(15))

    def test_multiplying_returns_fractions(self) -> None:
        result = Coordinate(f(2)).multiply(Coordinate(f(4)))
        assert isinstance(result[0], Fraction)

    def test_enforces_type(self) -> None:
        with pytest.raises(CoordinateError) as ce:
            # Try to mix fractions and floats
            Coordinate(f(1,2)).multiply(Coordinate(4.13)) # type: ignore
        assert "Cannot mix coordinates of different types." in str(ce.value)

    def test_multiply_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(f(1), f(2), f(3)).multiply(Coordinate(f(1)))

    def test_add(self) -> None:
        # Add on one dimension.
        assert Coordinate(f(1, 4)).add(Coordinate(f(2, 4)))[0] == f(3, 4)

        # Add on three dimensions.
        c: Coordinate = Coordinate(f(1), f(2), f(3)) + Coordinate(f(3), f(4), f(5))
        assert c == Coordinate(f(4),f(6),f(8))

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
        assert c == Coordinate(f(-2), f(3), f(5))

    def test_subtract_enforces_coordinate_size(self) -> None:
        with pytest.raises(CoordinateError):
            Coordinate(f(1), f(2), f(3)) - Coordinate(f(1))  # type: ignore

    def test_shift(self) -> None:
        a = Coordinate(f(1), f(2), f(3))
        b = Coordinate(f(3), f(4), f(5))
        c: Coordinate = a.shift(b)
        assert c == Coordinate(f(4), f(6), f(8))

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
        
class TestCoordinateConversions:
    def test_to_int(self) -> None:
        assert Coordinate(14, 7, 0, -2).to_ints() == Coordinate(14, 7, 0, -2)
        assert Coordinate(14.7, 79.0, 0.0, 1.1).to_ints() == Coordinate(14, 79, 0, 1)
        assert Coordinate(f(1, 2), f(1), f(3,4)).to_ints() == Coordinate(0, 1, 0)
        assert Coordinate(d(1.14), d(0), d(0.8999)).to_ints() == Coordinate(1, 0, 0)

    def test_to_floats(self) -> None:
        assert Coordinate(0.0, 14.2, -1.13).to_floats() == Coordinate(0.0, 14.2, -1.13)
        assert Coordinate(14, 7, 0, -2).to_floats() == Coordinate(14.0, 7.0, 0.0, -2.0)
        assert Coordinate(f(1, 2), f(1), f(3,4)).to_floats() == Coordinate(0.5, 1.0, 0.75)
        assert Coordinate(d(1.14), d(0), d(0.8999)).to_floats() == Coordinate(1.14, 0.0, 0.8999)

    def test_to_fractions(self) -> None:
        assert Coordinate(f(1), f(0), f(1, 2)).to_fractions() == Coordinate(f(1), f(0), f(1, 2))
        assert Coordinate(1, 0, 45, -1).to_fractions() == Coordinate(f(1), f(0), f(45), f(-1))
        assert Coordinate(7.2, 0.0, -0.5).to_fractions() == Coordinate(f(8106479329266893, 1125899906842624), f(0, 1), f(-1, 2) )
        assert Coordinate(d(1.14), d(0), d(0.8999)).to_fractions() == Coordinate(f(5134103575202365, 4503599627370496), f(0, 1), f(8105578609341419, 9007199254740992))

    def test_to_decimals(self) -> None:
        assert Coordinate(d(12.123), d(0), d(0.75)).to_decimals() == Coordinate(Decimal('12.1229999999999993320898283855058252811431884765625'), Decimal('0'), Decimal('0.75')).to_decimals()
        assert Coordinate(0.0, 14.2, -1.13).to_decimals() == Coordinate(Decimal('0'), Decimal('14.199999999999999289457264239899814128875732421875'), Decimal('-1.12999999999999989341858963598497211933135986328125'))
        assert Coordinate(1, 2, 3).to_decimals() == Coordinate(Decimal('1'), Decimal('2'), Decimal('3'))
        assert Coordinate(f(1,2)).to_decimals() == Coordinate(Decimal('0.5'))