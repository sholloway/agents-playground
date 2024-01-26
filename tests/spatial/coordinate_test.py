
from agents_playground.spatial.coordinate import Coordinate, Coordinate2d, Coordinate3d

class TestCoordinate2d:
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

  def test_subtract(self) -> None:
    a = Coordinate2d(1, 2)
    b = Coordinate2d(3, 4)
    c: Coordinate = a - b
    assert c[0] == -2
    assert c[1] == -2

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

class TestCoordinate3d:
  def test_multiply(self) -> None:
    a = Coordinate3d(1, 2, 3)
    b = Coordinate3d(3, 4, 5)
    c: Coordinate = a * b
    assert c[0] == 3
    assert c[1] == 8
    assert c[2] == 15

  def test_add(self) -> None:
    a = Coordinate3d(1, 2, 3)
    b = Coordinate3d(3, 4, 5)
    c: Coordinate = a + b
    assert c[0] == 4
    assert c[1] == 6
    assert c[2] == 8

  def test_subtract(self) -> None:
    a = Coordinate3d(1, 7, 10)
    b = Coordinate3d(3, 4, 5)
    c: Coordinate = a - b
    assert c[0] == -2
    assert c[1] == 3
    assert c[2] == 5

  def test_shift(self) -> None:
    a = Coordinate3d(1, 2, 3)
    b = Coordinate3d(3, 4, 5)
    c: Coordinate = a.shift(b)
    assert c[0] == 4
    assert c[1] == 6
    assert c[2] == 8

  def test_to_tuple(self) -> None:
    coord = Coordinate3d(17, 23, 1102)
    t = coord.to_tuple()
    assert t == (17, 23, 1102)

  def test_find_distance(self) -> None:
    a = Coordinate3d(12, 2, 7)
    b = Coordinate3d(93, 104, 14)

    distance = a.find_distance(b)
    assert a.find_distance(b) == b.find_distance(a)
    assert distance == 190