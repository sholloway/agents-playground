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
    def test_decimals(self, benchmark):
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
    def test_decimals(self, benchmark):
        benchmark(Decimal, "0.75")

    @pytest.mark.benchmark(group="Test From String", disable_gc=True)
    def test_fractions(self, benchmark):
        benchmark(Fraction, "0.75")


class TestSubtraction:
    @pytest.mark.benchmark(group="Test Subtraction", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(sub, 7, 9)
    
    @pytest.mark.benchmark(group="Test Subtraction", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(sub, 7.0, 9.0)

    @pytest.mark.benchmark(group="Test Subtraction", disable_gc=True)
    def test_decimals(self, benchmark):
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
    def test_decimals(self, benchmark):
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
    def test_decimals(self, benchmark):
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
    def test_decimals(self, benchmark):
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
    def test_decimals(self, benchmark):
        benchmark(eq, Decimal(17.4), Decimal(1.01))

    @pytest.mark.benchmark(group="Test Equality", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(3, 4)
        b = Fraction(1, 3)
        benchmark(eq, a, b)

class TestExponential:
    @pytest.mark.benchmark(group="Test Exponential", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(pow, 4, 2) 

    @pytest.mark.benchmark(group="Test Exponential", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(pow, 0.25, 2)
    
    @pytest.mark.benchmark(group="Test Exponential", disable_gc=True)
    def test_decimals(self, benchmark):
        benchmark(pow, Decimal(0.25), Decimal(2))

    @pytest.mark.benchmark(group="Test Exponential", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(1,4)
        benchmark(pow, a, 2)
    
class TestTruncate:
    @pytest.mark.benchmark(group="Test Truncate", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(trunc, 2)

    @pytest.mark.benchmark(group="Test Truncate", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(trunc, 2.3333333333333335)

    @pytest.mark.benchmark(group="Test Truncate", disable_gc=True)
    def test_decimals(self, benchmark):
        benchmark(trunc, Decimal(2.3333333333333335))

    @pytest.mark.benchmark(group="Test Truncate", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(7,3)
        benchmark(trunc, a)

class TestFloor:
    @pytest.mark.benchmark(group="Test Floor", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(floor, 2)
    
    @pytest.mark.benchmark(group="Test Floor", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(floor, 2.3333333333333335)

    @pytest.mark.benchmark(group="Test Floor", disable_gc=True)
    def test_decimals(self, benchmark):
        benchmark(floor, Decimal(2.3333333333333335))

    @pytest.mark.benchmark(group="Test Floor", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(7,3)
        benchmark(floor, a)

class TestCeil:
    @pytest.mark.benchmark(group="Test Ceil", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(ceil, 2)
    
    @pytest.mark.benchmark(group="Test Ceil", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(ceil, 2.3333333333333335)

    @pytest.mark.benchmark(group="Test Ceil", disable_gc=True)
    def test_decimals(self, benchmark):
        benchmark(ceil, Decimal(2.3333333333333335))

    @pytest.mark.benchmark(group="Test Ceil", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(7,3)
        benchmark(ceil, a)

class TestRound:
    @pytest.mark.benchmark(group="Test Round", disable_gc=True)
    def test_ints(self, benchmark):
        benchmark(round, 2, 2)
    
    @pytest.mark.benchmark(group="Test Round", disable_gc=True)
    def test_floats(self, benchmark):
        benchmark(round, 2.3333333333333335, 2)

    @pytest.mark.benchmark(group="Test Round", disable_gc=True)
    def test_decimals(self, benchmark):
        benchmark(round, Decimal(2.3333333333333335), 2)
    
    @pytest.mark.benchmark(group="Test Round", disable_gc=True)
    def test_fractions(self, benchmark):
        a = Fraction(7,3)
        benchmark(round, a, 2)