import pytest

from decimal import Decimal, getcontext
from fractions import Fraction
from operator import add, sub, mul, truediv, eq, pow
from math import pi, sqrt, trunc, floor, ceil

getcontext().prec = 6

class TestInitialization:
    @pytest.mark.benchmark(group="Test Initialization", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(int, 0.75)

    @pytest.mark.benchmark(group="Test Initialization", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(float, 0.75)

    @pytest.mark.benchmark(group="Test Initialization", disable_gc=True)
    def test_decimal(self, benchmark):
        benchmark(Decimal, 0.75)

    @pytest.mark.benchmark(group="Test Initialization", disable_gc=True)
    def test_fractions(self, benchmark):
        benchmark(Fraction, 3, 4)

class TestFromString:
    @pytest.mark.benchmark(group="Test From String", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(int, "1")

    @pytest.mark.benchmark(group="Test From String", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(float, "0.75")

    @pytest.mark.benchmark(group="Test From String", disable_gc=True)
    def test_decimal(self, benchmark):
        benchmark(Decimal, "0.75")

    @pytest.mark.benchmark(group="Test From String", disable_gc=True)
    def test_fractions(self, benchmark):
        benchmark(Fraction, "0.75")

class TestAddition:
    @pytest.mark.benchmark(group="Test Addition", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(add, 7, 9)

    @pytest.mark.benchmark(group="Test Addition", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(add, 7.0, 9.0)

    @pytest.mark.benchmark(group="Test Addition", disable_gc=True)
    def test_decimal(self, benchmark):
        benchmark(add, Decimal(7), Decimal(9))

    @pytest.mark.benchmark(group="Test Addition", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(add, a, b)

class TestSubtraction:
    @pytest.mark.benchmark(group="Test Subtraction", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(sub, 7, 9)
    
    @pytest.mark.benchmark(group="Test Subtraction", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(sub, 7.0, 9.0)

    @pytest.mark.benchmark(group="Test Subtraction", disable_gc=True)
    def test_decimal(self, benchmark):
        benchmark(sub, Decimal(7), Decimal(9))

    @pytest.mark.benchmark(group="Test Subtraction", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(sub, a, b)

class TestMultiplication:
    @pytest.mark.benchmark(group="Test Multiplication", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(mul, 7, 9)

    @pytest.mark.benchmark(group="Test Multiplication", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(mul, 7.0, 9.0)

    @pytest.mark.benchmark(group="Test Multiplication", disable_gc=True)
    def test_decimal(self, benchmark):
        benchmark(mul, Decimal(7), Decimal(9))

    @pytest.mark.benchmark(group="Test Multiplication", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(mul, a, b)

class TestDivision:
    @pytest.mark.benchmark(group="Test Division", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(truediv, 7, 9)

    @pytest.mark.benchmark(group="Test Division", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(truediv, 7.0, 9.0)

    @pytest.mark.benchmark(group="Test Division", disable_gc=True)
    def test_decimal(self, benchmark):
        benchmark(truediv, Decimal(7), Decimal(9))

    @pytest.mark.benchmark(group="Test Division", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(truediv, a, b)

class TestSquareRoot:
    @pytest.mark.benchmark(group="Test Square Root", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(sqrt, 2)

    @pytest.mark.benchmark(group="Test Square Root", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(sqrt, 2.0)

    @pytest.mark.benchmark(group="Test Square Root", disable_gc=True)
    def test_decimal(self, benchmark):
        benchmark(sqrt, Decimal(2))

    @pytest.mark.benchmark(group="Test Square Root", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(3, 4)
        benchmark(sqrt, a)

class TestEquality:
    @pytest.mark.benchmark(group="Test Equality", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(eq, 17, 1)

    @pytest.mark.benchmark(group="Test Equality", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(eq, 17.4, 1.01)

    @pytest.mark.benchmark(group="Test Equality", disable_gc=True)
    def test_decimal(self, benchmark):
        benchmark(eq, Decimal(17.4), Decimal(1.01))

    @pytest.mark.benchmark(group="Test Equality", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(eq, a, b)

class TestIsClose:
    # Test Math.isclose()
    pass

class TestExponential:
    @pytest.mark.benchmark(group="Test Exponential", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(pow, 4, 2) 

    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(pow, 0.25, 2)
    
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_decimal(self, benchmark):
        benchmark(pow, Decimal(0.25), Decimal(2))

    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(pi)
        benchmark(a.limit_denominator, 10)
    

class TestFloats:
    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_truncate(self, benchmark):
        benchmark(trunc, 2.3333333333333335)
    
    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_floor(self, benchmark):
        benchmark(floor, 2.3333333333333335)
    
    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_ceil(self, benchmark):
        benchmark(ceil, 2.3333333333333335)
    
    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_round(self, benchmark):
        benchmark(round, 2.3333333333333335, 2)


class TestDecimal:
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_truncate(self, benchmark):
        benchmark(trunc, Decimal(2.3333333333333335))
    
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_floor(self, benchmark):
        benchmark(floor, Decimal(2.3333333333333335))
    
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_ceil(self, benchmark):
        benchmark(ceil, Decimal(2.3333333333333335))
    
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_round(self, benchmark):
        benchmark(round, Decimal(2.3333333333333335), 2)

class TestFractions:
    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_exponential(self, benchmark):
        a = Fraction(1,4)
        benchmark(pow, a, 2)
    
    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_truncate(self, benchmark):
        a = Fraction(7,3)
        benchmark(trunc, a)

    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_floor(self, benchmark):
        a = Fraction(7,3)
        benchmark(floor, a)
    
    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_ceil(self, benchmark):
        a = Fraction(7,3)
        benchmark(ceil, a)
    
    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_round(self, benchmark):
        a = Fraction(7,3)
        benchmark(round, a, 2)