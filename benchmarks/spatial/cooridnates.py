from operator import add, mul, sub
import pytest
from agents_playground.spatial.coordinate import Coordinate

class TestCoordinateInit:
    # Temporary class to see how the decorators impact the performance of Coordinates.
    @pytest.mark.benchmark(group="Coordinate Initialization", disable_gc=True)
    def test_1d(self, benchmark) -> None:
        benchmark(Coordinate, 1)
    
    @pytest.mark.benchmark(group="Coordinate Initialization", disable_gc=True)
    def test_2d(self, benchmark) -> None:
        benchmark(Coordinate, 1, 2)
    
    @pytest.mark.benchmark(group="Coordinate Initialization", disable_gc=True)
    def test_3d(self, benchmark) -> None:
        benchmark(Coordinate, 1, 2, 3)
    
    @pytest.mark.benchmark(group="Coordinate Initialization", disable_gc=True)
    def test_4d(self, benchmark) -> None:
        benchmark(Coordinate, 1, 2, 3, 4)

class TestCoordinateAddition:
    # Temporary class to see how the decorators impact the performance of Coordinates.
    @pytest.mark.benchmark(group="Coordinate Addition", disable_gc=True)
    def test_1d(self, benchmark) -> None:
        a = Coordinate(1.0)
        b = Coordinate(7.2)
        benchmark(add, a, b)
    
    @pytest.mark.benchmark(group="Coordinate Addition", disable_gc=True)
    def test_2d(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19)
        b = Coordinate(7.2, 42.0)
        benchmark(add, a, b)
    
    @pytest.mark.benchmark(group="Coordinate Addition", disable_gc=True)
    def test_3d(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19, 192.1)
        b = Coordinate(7.2, 42.0, 33.333)
        benchmark(add, a, b)
    
    @pytest.mark.benchmark(group="Coordinate Addition", disable_gc=True)
    def test_4d(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19, 192.1, 1.0)
        b = Coordinate(7.2, 42.0, 33.333, 1.0)
        benchmark(add, a, b)

class TestCoordinateSubtraction:
    # Temporary class to see how the decorators impact the performance of Coordinates.
    @pytest.mark.benchmark(group="Coordinate Subtraction", disable_gc=True)
    def test_1d(self, benchmark) -> None:
        a = Coordinate(1.0)
        b = Coordinate(7.2)
        benchmark(sub, a, b)
    
    @pytest.mark.benchmark(group="Coordinate Subtraction", disable_gc=True)
    def test_2d(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19)
        b = Coordinate(7.2, 42.0)
        benchmark(sub, a, b)
    
    @pytest.mark.benchmark(group="Coordinate Subtraction", disable_gc=True)
    def test_3d(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19, 192.1)
        b = Coordinate(7.2, 42.0, 33.333)
        benchmark(sub, a, b)
    
    @pytest.mark.benchmark(group="Coordinate Subtraction", disable_gc=True)
    def test_4d(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19, 192.1, 1.0)
        b = Coordinate(7.2, 42.0, 33.333, 1.0)
        benchmark(sub, a, b)

class TestCoordinateMultiplication:
    # Temporary class to see how the decorators impact the performance of Coordinates.
    @pytest.mark.benchmark(group="Coordinate Multiplication", disable_gc=True)
    def test_1d(self, benchmark) -> None:
        a = Coordinate(1.0)
        b = Coordinate(7.2)
        benchmark(mul, a, b)
    
    @pytest.mark.benchmark(group="Coordinate Multiplication", disable_gc=True)
    def test_2d(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19)
        b = Coordinate(7.2, 42.0)
        benchmark(mul, a, b)
    
    @pytest.mark.benchmark(group="Coordinate Multiplication", disable_gc=True)
    def test_3d(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19, 192.1)
        b = Coordinate(7.2, 42.0, 33.333)
        benchmark(mul, a, b)
    
    @pytest.mark.benchmark(group="Coordinate Multiplication", disable_gc=True)
    def test_4d(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19, 192.1, 1.0)
        b = Coordinate(7.2, 42.0, 33.333, 1.0)
        benchmark(mul, a, b)