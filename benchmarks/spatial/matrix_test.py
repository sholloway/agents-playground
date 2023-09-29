# from pytest_benchmark import 
import pytest
from agents_playground.spatial.matrix2x2 import m2, Matrix2x2
from agents_playground.spatial.matrix3x3 import m3, Matrix3x3
from agents_playground.spatial.matrix4x4 import m4, Matrix4x4

@pytest.fixture
def ordered_values(): 
  return [1, 2, 3, 4,
    5, 6, 7, 8, 
    9, 10, 11, 12,
    13, 14, 15, 16]

class TestMatrixInitialization:
  @pytest.mark.benchmark(group="Matrix Initialization", disable_gc=True)
  def test_m2(self, benchmark, ordered_values) -> None:
    benchmark(m2, *ordered_values[0:4])

  @pytest.mark.benchmark(group="Matrix Initialization", disable_gc=True)
  def test_m3(self, benchmark, ordered_values) -> None:
    benchmark(m3, *ordered_values[0:9])

  @pytest.mark.benchmark(group="Matrix Initialization", disable_gc=True)
  def test_m4(self, benchmark, ordered_values) -> None:
    benchmark(m4, *ordered_values)


class TestMatrixTranspose:
  @pytest.mark.benchmark(group="Matrix Transpose", disable_gc=True)
  def test_2x2(self, benchmark, ordered_values) -> None:
    m = m2(*ordered_values[0:4])
    benchmark(m.transpose)
  
  @pytest.mark.benchmark(group="Matrix Transpose", disable_gc=True)
  def test_3x3(self, benchmark, ordered_values) -> None:
    m = m3(*ordered_values[0:9])
    benchmark(m.transpose)
  
  @pytest.mark.benchmark(group="Matrix Transpose", disable_gc=True)
  def test_4x4(self, benchmark, ordered_values) -> None:
    m = m4(*ordered_values)
    benchmark(m.transpose)