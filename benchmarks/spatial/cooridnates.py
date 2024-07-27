from __future__ import annotations

from functools import reduce
import itertools
import math
from operator import add, mul, sub
from typing import Iterator
import pytest
from agents_playground.spatial.coordinate import Coordinate

class CoordinateBaseline:
    # Note this only works with floats.
    def __init__(self, *components: float) -> None:
        self._components: tuple[float, ...] = components

    def to_tuple(self) -> tuple[float, ...]:
        return tuple(self._components)

    def __len__(self) -> int:
        return len(self._components)

    def __getitem__(self, lookup: int) -> float:
        return self._components[lookup]

    def __eq__(self, other: CoordinateBaseline) -> bool:
        close: Iterator[bool] = itertools.starmap(
            math.isclose, zip(self, other)
        )
        return all(close)

    def __repr__(self) -> str:
        return f"Coordinate{self._components}"

    def __hash__(self) -> int:
        return self._components.__hash__()

    def __mul__(
        self, other: CoordinateBaseline
    ) -> CoordinateBaseline:
        products = itertools.starmap(
            mul, zip(self, other)
        )
        return CoordinateBaseline(*products)

    def __add__(
        self, other: CoordinateBaseline
    ) -> CoordinateBaseline:
        sums = itertools.starmap(add, zip(self, other))
        return CoordinateBaseline(*sums)

    def __sub__(
        self, other: CoordinateBaseline
    ) -> CoordinateBaseline:
        diffs = itertools.starmap(sub, zip(self, other))
        return CoordinateBaseline(*diffs)

    def find_manhattan_distance(
        self, other: CoordinateBaseline
    ) -> float:
        """Finds the Manhattan distance between two locations."""
        differences = itertools.starmap(
            sub, zip(self, other)
        )
        return reduce(lambda a, b: abs(a) + abs(b), differences)
    
    def find_euclidean_distance(
        self, other: CoordinateBaseline
    ) -> float:
        """Finds the Euclidean distance (as the crow flies) between two locations."""
        differences = itertools.starmap(
            sub, zip(self, other)
        )
        squared_differences = list(map(lambda i: i * i, differences))
        summation = reduce(add, squared_differences)
        return math.sqrt(summation)

    def __iter__(self) -> Iterator[float]:
        return iter(self._components)

class TestCoordinateInit:
    @pytest.mark.benchmark(group="Coordinate Initialization", disable_gc=True)
    def test_baseline(self, benchmark) -> None:
        benchmark(CoordinateBaseline, 1.0, 2.0, 3.0, 4.0)
    
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
    @pytest.mark.benchmark(group="Coordinate Addition", disable_gc=True)
    def test_baseline(self, benchmark) -> None:
        a = CoordinateBaseline(1.0, 3.19, 192.1, 1.0)
        b = CoordinateBaseline(1.0, 3.19, 192.1, 1.0)
        benchmark(add, a, b)
    
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
    @pytest.mark.benchmark(group="Coordinate Subtraction", disable_gc=True)
    def test_baseline(self, benchmark) -> None:
        a = CoordinateBaseline(1.0, 3.19, 192.1, 1.0)
        b = CoordinateBaseline(7.2, 42.0, 33.333, 1.0)
        benchmark(sub, a, b)
    
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
    @pytest.mark.benchmark(group="Coordinate Multiplication", disable_gc=True)
    def test_baseline(self, benchmark) -> None:
        a = CoordinateBaseline(1.0, 3.19, 192.1, 1.0)
        b = CoordinateBaseline(7.2, 42.0, 33.333, 1.0)
        benchmark(mul, a, b)
    
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

class TestCoordinateDistance:
    @pytest.mark.benchmark(group="Coordinate Distance", disable_gc=True)
    def test_manhattan_baseline(self, benchmark) -> None:
        a = CoordinateBaseline(1.0, 3.19, 192.1)
        b = CoordinateBaseline(7.2, 42.0, 33.333)
        benchmark(a.find_manhattan_distance, b)
    
    @pytest.mark.benchmark(group="Coordinate Distance", disable_gc=True)
    def test_euclidean_baseline(self, benchmark) -> None:
        a = CoordinateBaseline(1.0, 3.19, 192.1)
        b = CoordinateBaseline(7.2, 42.0, 33.333)
        benchmark(a.find_euclidean_distance, b)

    @pytest.mark.benchmark(group="Coordinate Distance", disable_gc=True)
    def test_manhattan(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19, 192.1)
        b = Coordinate(7.2, 42.0, 33.333)
        benchmark(a.find_manhattan_distance, b)
    
    @pytest.mark.benchmark(group="Coordinate Distance", disable_gc=True)
    def test_euclidean(self, benchmark) -> None:
        a = Coordinate(1.0, 3.19, 192.1)
        b = Coordinate(7.2, 42.0, 33.333)
        benchmark(a.find_euclidean_distance, b)