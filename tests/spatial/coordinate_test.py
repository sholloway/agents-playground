
from agents_playground.spatial.coordinate import Coordinate, Coordinate2d


class TestCoordinate:
  def test_multiply(self) -> None:
    a = Coordinate2d(1, 2)
    b = Coordinate2d(3, 4)
    c: Coordinate = a * b
    assert c[0] == 3
    assert c[1] == 8

  def test_add(self) -> None:
    a = Coordinate2d(1, 2)
    b = Coordinate2d(3, 4)
    c: Coordinate = a + b
    assert c[0] == 4
    assert c[1] == 6

  def test_shift(self) -> None:
    a = Coordinate2d(1, 2)
    b = Coordinate2d(3, 4)
    c: Coordinate = a.shift(b)
    assert c[0] == 4
    assert c[1] == 6

  def test_to_tuple(self) -> None:
    coord = Coordinate2d(17, 23)
    t = coord.to_tuple()
    assert t == (17, 23)

  def test_find_distance(self) -> None:
    a = Coordinate2d(12, 2)
    b = Coordinate2d(93, 104)

    distance = a.find_distance(b)
    assert a.find_distance(b) == b.find_distance(a)
    assert distance == 183