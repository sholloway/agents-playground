from typing import Protocol, Tuple

from deprecated import deprecated  # type: ignore


@deprecated(reason="Deprecated in favor of Coordinate.")
class Vertex(Protocol):
    """
    A base level vertex. Used to define lattices such as triangles and polygons.

    Vertices are always specified in canvas space. Not Grid Coordinates.
    Coordinates are stored in traditional alphabetic order (x, y, z,...).
    """

    coordinates: Tuple[float, ...]

    def __len__(self) -> int:
        return len(self.coordinates)


@deprecated(reason="Deprecated in favor of Coordinate.")
class Vertex2d(Vertex):
    """
    A two dimensional vertex.
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        self.coordinates = (x, y)


@deprecated(reason="Deprecated in favor of Coordinate.")
class Vertex3d(Vertex):
    """
    A three dimensional vertex.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        super().__init__()
        self.coordinates = (x, y, z)
