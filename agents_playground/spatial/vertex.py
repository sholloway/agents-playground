from typing import Protocol, Tuple

class Vertex(Protocol):
  """
  A base level vertex. Used to define lattices such as triangles and polygons.

  Vertices are always specified in canvas space. Not Grid Coordinates.
  Coordinates are stored in traditional alphabetic order (x, y, z,...).
  """
  coordinates: Tuple[float, ...]

class Vertex2d(Vertex):
  """
  A two dimensional vertex.
  """
  def __init__(self, x: float, y: float) -> None:
    self.coordinates = (x, y)

class Vertex3d(Vertex):
  """
  A three dimensional vertex.
  """
  def __init__(self, x: float, y: float, z: float) -> None:
    self.coordinates = (x, y, z)