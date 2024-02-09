
import pytest
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import MeshLike
from agents_playground.spatial.mesh.half_edge_mesh import HalfEdgeMesh, MeshWindingDirection

from agents_playground.spatial.mesh.tesselator import SimpleFanTesselator, Tesselator

@pytest.fixture
def polygon_a() -> list[Coordinate]:
  return[
    Coordinate(2, 3), # Vertex 1
    Coordinate(6, 6), # Vertex 2
    Coordinate(9, 3), # Vertex 3
    Coordinate(5, 1), # Vertex 4
  ]

class TestTesselator:
  def test_make_fans(self, polygon_a) -> None:
    """
    Test a simple tesselation scheme. Given a polygon, make a fan of triangles.
    """

    mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CW)
    mesh.add_polygon(polygon_a)

    assert mesh.num_vertices() == 4
    assert mesh.num_faces() == 1
    assert mesh.num_edges() == 4

    tess: Tesselator = SimpleFanTesselator()
    tess.tesselate(mesh)

    assert mesh.num_vertices() == 4
    assert mesh.num_faces() == 2
    assert mesh.num_edges() == 5