
import pytest

from math import atan2, degrees, radians

from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import MeshLike
from agents_playground.spatial.mesh.half_edge_mesh import HalfEdgeMesh, MeshVertex, MeshWindingDirection

from agents_playground.spatial.mesh.tesselator import FanTesselator, Tesselator, is_convex

@pytest.fixture
def polygon_a() -> list[Coordinate]:
  """A 2D convex, 4 sided polygon."""
  return[
    Coordinate(2, 3), # Vertex 1
    Coordinate(6, 6), # Vertex 2
    Coordinate(9, 3), # Vertex 3
    Coordinate(5, 1), # Vertex 4
  ]

@pytest.fixture
def polygon_b() -> list[Coordinate]:
  """A 2D concave, 5 sided polygon."""
  return[
    Coordinate(2, 3), # Vertex 1
    Coordinate(6, 6), # Vertex 2
    Coordinate(9, 3), # Vertex 3
    Coordinate(5, 1), # Vertex 4
    Coordinate(5, 3), # Vertex 5
  ]

@pytest.fixture
def polygon_aa() -> list[Coordinate]:
  """A 3D convex, 4 sided polygon."""
  return[
    Coordinate(2, 3, 10), # Vertex 1
    Coordinate(6, 6, 10), # Vertex 2
    Coordinate(9, 3, 10), # Vertex 3
    Coordinate(5, 1, 10), # Vertex 4
  ]

@pytest.fixture
def polygon_bb() -> list[Coordinate]:
  """A 3D concave, 5 sided polygon."""
  return[
    Coordinate(2, 3, -4), # Vertex 1
    Coordinate(6, 6, -4), # Vertex 2
    Coordinate(9, 3, -4), # Vertex 3
    Coordinate(5, 1, -4), # Vertex 4
    Coordinate(5, 3, -4), # Vertex 5
  ]

@pytest.fixture
def polygon_cube() -> list[Coordinate]:
  """A 3D concave, 5 sided polygon."""
  return[
    Coordinate(2, 3, -4), # Vertex 1
    Coordinate(6, 6, -4), # Vertex 2
    Coordinate(9, 3, -4), # Vertex 3
    Coordinate(5, 1, -4), # Vertex 4
    Coordinate(5, 3, -4), # Vertex 5
  ]



class TestTesselator:
  def test_make_fans(self, polygon_a: list[Coordinate]) -> None:
    """
    Test a simple tesselation scheme. Given a polygon, make a fan of triangles.
    """

    mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)

    assert mesh.num_vertices() == 4
    assert mesh.num_faces() == 1
    assert mesh.num_edges() == 4

    tess: Tesselator = FanTesselator()
    tess.tesselate(mesh)

    assert mesh.num_vertices() == 4
    assert mesh.num_faces() == 2
    assert mesh.num_edges() == 5

  def test_is_convex_2d(self, polygon_a: list[Coordinate], polygon_b: list[Coordinate]) -> None:
    assert is_convex([ MeshVertex(coord, index) for index, coord in enumerate(polygon_a) ])
    assert not is_convex([ MeshVertex(coord, index) for index, coord in enumerate(polygon_b) ])

  def test_is_convex_3d(self, polygon_aa: list[Coordinate], polygon_bb: list[Coordinate]) -> None:
    assert is_convex([ MeshVertex(coord, index) for index, coord in enumerate(polygon_aa) ])
    assert not is_convex([ MeshVertex(coord, index) for index, coord in enumerate(polygon_bb) ])
