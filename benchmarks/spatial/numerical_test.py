import pytest

from decimal import Decimal, getcontext
from fractions import Fraction
from operator import add, sub, mul, truediv, eq, pow
from math import pi, sqrt, trunc, floor, ceil

class TestInts:
    @pytest.mark.benchmark(group="Test Ints", disable_gc=True)
    def test_initialization(self, benchmark):
        benchmark(int, 0.75)
    
    @pytest.mark.benchmark(group="Test Ints", disable_gc=True)
    def test_init_from_str(self, benchmark):
        benchmark(int, "1")

    @pytest.mark.benchmark(group="Test Ints", disable_gc=True)
    def test_addition(self, benchmark):
        benchmark(add, 7, 9)

    @pytest.mark.benchmark(group="Test Ints", disable_gc=True)
    def test_subtraction(self, benchmark):
        benchmark(sub, 7, 9)

    @pytest.mark.benchmark(group="Test Ints", disable_gc=True)
    def test_multiplication(self, benchmark):
        benchmark(mul, 7, 9)

    @pytest.mark.benchmark(group="Test Ints", disable_gc=True)
    def test_division(self, benchmark):
        benchmark(truediv, 7, 9)
    
    @pytest.mark.benchmark(group="Test Ints", disable_gc=True)
    def test_sqrt(self, benchmark):
        benchmark(sqrt, 2)
    
    @pytest.mark.benchmark(group="Test Ints", disable_gc=True)
    def test_equality(self, benchmark):
        benchmark(eq, 17, 1)
    
    @pytest.mark.benchmark(group="Test Ints", disable_gc=True)
    def test_exponential(self, benchmark):
        benchmark(pow, 4, 2)

class TestFloats:
    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_initialization(self, benchmark):
        benchmark(float, 0.75)
    
    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_init_from_str(self, benchmark):
        benchmark(float, "0.75")

    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_addition(self, benchmark):
        benchmark(add, 7.0, 9.0)

    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_subtraction(self, benchmark):
        benchmark(sub, 7.0, 9.0)

    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_multiplication(self, benchmark):
        benchmark(mul, 7.0, 9.0)

    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_division(self, benchmark):
        benchmark(truediv, 7.0, 9.0)
    
    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_sqrt(self, benchmark):
        benchmark(sqrt, 2.0)
    
    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_equality(self, benchmark):
        benchmark(eq, 17.4, 1.01)
    
    @pytest.mark.benchmark(group="Test Floats", disable_gc=True)
    def test_exponential(self, benchmark):
        benchmark(pow, 0.25, 2)
    
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

getcontext().prec = 6
class TestDecimal:
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_initialization(self, benchmark):
        benchmark(Decimal, 0.75)
    
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_init_from_str(self, benchmark):
        benchmark(Decimal, "0.75")

    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_addition(self, benchmark):
        benchmark(add, Decimal(7), Decimal(9))

    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_subtraction(self, benchmark):
        benchmark(sub, Decimal(7), Decimal(9))

    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_multiplication(self, benchmark):
        benchmark(mul, Decimal(7), Decimal(9))

    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_division(self, benchmark):
        benchmark(truediv, Decimal(7), Decimal(9))
    
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_sqrt(self, benchmark):
        benchmark(sqrt, Decimal(2))
    
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_equality(self, benchmark):
        benchmark(eq, Decimal(17.4), Decimal(1.01))
    
    @pytest.mark.benchmark(group="Test Decimal", disable_gc=True)
    def test_exponential(self, benchmark):
        benchmark(pow, Decimal(0.25), Decimal(2))
    
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
    def test_initialization(self, benchmark):
        benchmark(Fraction, 3, 4)

    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_init_from_str(self, benchmark):
        benchmark(Fraction, "0.75")

    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_addition(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(add, a, b)

    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_subtraction(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(sub, a, b)

    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_multiplication(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(mul, a, b)

    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_division(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(truediv, a, b)
    
    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_sqrt(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(sqrt, a)
    
    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_equality(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(eq, a, b)
    
    @pytest.mark.benchmark(group="Test Fractions", disable_gc=True)
    def test_find_nearest_rational(self, benchmark):
        a = Fraction(pi)
        benchmark(a.limit_denominator, 10)
    
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