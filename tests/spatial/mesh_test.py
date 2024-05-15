import os
from pathlib import Path
from typing import Callable
import pytest
from agents_playground.counter.counter import Counter, CounterBuilder

from agents_playground.fp import Nothing
from agents_playground.loaders.obj_loader import Obj, ObjLoader
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape import Landscape, cubic_tile_to_vertices
from agents_playground.spatial.landscape.constants import STANDARD_GRAVITY_IN_METRIC
from agents_playground.spatial.landscape.landscape_characteristics import (
    LandscapeCharacteristics,
)
from agents_playground.spatial.landscape.landscape_physicality import (
    LandscapePhysicality,
)
from agents_playground.spatial.landscape.tile import (
    Tile,
    TileCubicPlacement,
    TileCubicVerticesPlacement,
)
from agents_playground.spatial.landscape.types import (
    LandscapeGravityUOM,
    LandscapeMeshType,
)
from agents_playground.spatial.mesh import (
    UNSET_MESH_ID,
    MeshFaceLike,
    MeshHalfEdgeLike,
    MeshLike,
    MeshVertexLike,
)
from agents_playground.spatial.mesh.half_edge_mesh import (
    HalfEdgeMesh,
    MeshException,
    MeshWindingDirection,
    obj_to_mesh,
)
from agents_playground.spatial.mesh.printer import MeshTablePrinter

from agents_playground.spatial.vector.vector3d import Vector3d
from agents_playground.uom import LengthUOM, SystemOfMeasurement


@pytest.fixture
def lc() -> LandscapeCharacteristics:
    return LandscapeCharacteristics(
        mesh_type=LandscapeMeshType.SQUARE_TILE,
        landscape_uom_system=SystemOfMeasurement.METRIC,
        tile_size_uom=LengthUOM.METER,
        tile_width=1,
        tile_height=1,
        tile_depth=1,
    )


@pytest.fixture
def linear_landscape_strip(lc: LandscapeCharacteristics) -> Landscape:
    """
    Creates a landscape defined as a strip of tiles on the X-axis.
    """
    physicality = LandscapePhysicality(
        gravity_uom=LandscapeGravityUOM.METERS_PER_SECOND_SQUARED,
        gravity_strength=STANDARD_GRAVITY_IN_METRIC,
    )

    # A list of tile coordinates in the form (x,y,z,volume placement)
    tile_locations: list[tuple[int, ...]] = [
        (0, 0, 0, TileCubicPlacement.BOTTOM),
        (1, 0, 0, TileCubicPlacement.BOTTOM),
        (2, 0, 0, TileCubicPlacement.BOTTOM),
        (3, 0, 0, TileCubicPlacement.BOTTOM),
        (4, 0, 0, TileCubicPlacement.BOTTOM),
        (5, 0, 0, TileCubicPlacement.BOTTOM),
    ]

    tiles: list[Tile] = [Tile(Coordinate(*t)) for t in tile_locations]

    return Landscape(
        file_characteristics=Nothing(),
        characteristics=lc,
        physicality=physicality,
        custom_attributes={},
        tiles={
            t.location: t for t in tiles
        },  # Build a dict with the tile location as the key.
    )


@pytest.fixture
def plane_with_changing_y_value(lc: LandscapeCharacteristics) -> Landscape:
    """
    A landscape with it's y-axis value changed.
    """
    physicality = LandscapePhysicality(
        gravity_uom=LandscapeGravityUOM.METERS_PER_SECOND_SQUARED,
        gravity_strength=STANDARD_GRAVITY_IN_METRIC,
    )

    # A list of tile coordinates in the form (x,y,z,volume placement)
    tile_locations: list[tuple[int, ...]] = [
        (0, 0, 0, 3),
        (0, 2, 1, 3),
        (0, 0, 2, 3),
        (0, 1, 3, 3),
        (0, 0, 4, 3),
        (0, 0, 5, 3),
        (0, 1, 6, 3),
        (0, 0, 7, 3),
        (0, 2, 8, 3),
        (0, 0, 9, 3),
        (1, 0, 0, 3),
        (1, 1, 1, 3),
        (1, 0, 2, 3),
        (1, 0, 3, 3),
        (1, 0, 4, 3),
        (1, 0, 5, 3),
        (1, 0, 6, 3),
        (1, 1, 7, 3),
        (1, 0, 8, 3),
        (1, 0, 9, 3),
        (2, 0, 0, 3),
        (2, 1, 1, 3),
        (2, 0, 2, 3),
        (2, 0, 3, 3),
        (2, 0, 4, 3),
        (2, 0, 5, 3),
        (2, 0, 6, 3),
        (2, 0, 7, 3),
        (2, 1, 8, 3),
        (2, 1, 9, 3),
        (3, 1, 0, 3),
        (3, 0, 1, 3),
        (3, 0, 2, 3),
        (3, 0, 3, 3),
        (3, 0, 4, 3),
        (3, 0, 5, 3),
        (3, 0, 6, 3),
        (3, 1, 7, 3),
        (3, 2, 8, 3),
        (3, 0, 9, 3),
        (4, 0, 0, 3),
        (4, 0, 1, 3),
        (4, 0, 2, 3),
        (4, 0, 3, 3),
        (4, 0, 4, 3),
        (4, 0, 5, 3),
        (4, 0, 6, 3),
        (4, 2, 7, 3),
        (4, 1, 8, 3),
        (4, 1, 9, 3),
        (5, 0, 0, 3),
        (5, 0, 1, 3),
        (5, 1, 2, 3),
        (5, 0, 3, 3),
        (5, 0, 4, 3),
        (5, 0, 5, 3),
        (5, 0, 6, 3),
        (5, 0, 7, 3),
        (5, 0, 8, 3),
        (5, 0, 9, 3),
        (6, 0, 0, 3),
        (6, 0, 1, 3),
        (6, 0, 2, 3),
        (6, 0, 3, 3),
        (6, 0, 4, 3),
        (6, 1, 5, 3),
        (6, 0, 6, 3),
        (6, 0, 7, 3),
        (6, 0, 8, 3),
        (6, 2, 9, 3),
        (7, 0, 0, 3),
        (7, 0, 1, 3),
        (7, 2, 2, 3),
        (7, 0, 3, 3),
        (7, 0, 4, 3),
        (7, 0, 5, 3),
        (7, 0, 6, 3),
        (7, 0, 7, 3),
        (7, 0, 8, 3),
        (7, 0, 9, 3),
    ]

    tiles: list[Tile] = [Tile(Coordinate(*t)) for t in tile_locations]

    return Landscape(
        file_characteristics=Nothing(),
        characteristics=lc,
        physicality=physicality,
        custom_attributes={},
        tiles={
            t.location: t for t in tiles
        },  # Build a dict with the tile location as the key.
    )


@pytest.fixture
def landscape_cube(lc: LandscapeCharacteristics) -> Landscape:
    """
    Creates a landscape defined by 6 tiles
    """
    physicality = LandscapePhysicality(
        gravity_uom=LandscapeGravityUOM.METERS_PER_SECOND_SQUARED,
        gravity_strength=STANDARD_GRAVITY_IN_METRIC,
    )

    # A list of tile coordinates in the form (x,y,z,volume placement)
    tile_locations: list[tuple[int, ...]] = [
        (0, 0, 0, TileCubicPlacement.BOTTOM),  # Face 1
        (0, 0, 0, TileCubicPlacement.TOP),  # Face 2
        (0, 0, 0, TileCubicPlacement.FRONT),  # Face 3
        (0, 0, 0, TileCubicPlacement.BACK),  # Face 4
        (0, 0, 0, TileCubicPlacement.LEFT),  # Face 5
        (0, 0, 0, TileCubicPlacement.RIGHT),  # Face 6
    ]

    tiles: list[Tile] = [Tile(Coordinate(*t)) for t in tile_locations]

    return Landscape(
        file_characteristics=Nothing(),
        characteristics=lc,
        physicality=physicality,
        custom_attributes={},
        tiles={
            t.location: t for t in tiles
        },  # Build a dict with the tile location as the key.
    )


@pytest.fixture
def polygon_a() -> list[Coordinate]:
    return [
        Coordinate(2, 3),  # Vertex 1
        Coordinate(6, 6),  # Vertex 2
        Coordinate(9, 3),  # Vertex 3
        Coordinate(5, 1),  # Vertex 4
    ]


@pytest.fixture
def polygon_b() -> list[Coordinate]:
    return [
        Coordinate(9, 3),  # Shared Vertex 3
        Coordinate(6, 6),  # Shared Vertex 2
        Coordinate(10, 7),  # Vertex 5
        Coordinate(13, 4),  # Vertex 6
    ]


@pytest.fixture
def polygon_c() -> list[Coordinate]:
    return [
        Coordinate(9, 3),  # Shared Vertex 3
        Coordinate(13, 4),  # Shared Vertex 6
        Coordinate(14, 1),  # Vertex 7
        Coordinate(10, 1),  # Vertex 8
    ]


class TestHalfEdgeMesh:
    def test_polygon_winding(self) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        assert mesh.winding == MeshWindingDirection.CCW

    def test_tile_to_vertices_with_bottom_tiles(
        self, lc: LandscapeCharacteristics
    ) -> None:
        at_origin = Tile(Coordinate(0, 0, 0, TileCubicPlacement.BOTTOM))
        at_origin_tile_vertices: list[Coordinate] = cubic_tile_to_vertices(
            at_origin, lc
        )
        assert len(at_origin_tile_vertices) == 4
        assert at_origin_tile_vertices[0] == Coordinate(1, 0, 1)  # F
        assert at_origin_tile_vertices[1] == Coordinate(1, 0, 0)  # B
        assert at_origin_tile_vertices[2] == Coordinate(0, 0, 0)  # C
        assert at_origin_tile_vertices[3] == Coordinate(0, 0, 1)  # G

        shifted_on_x_axis_tile = Tile(Coordinate(4, 0, 0, TileCubicPlacement.BOTTOM))
        shifted_on_x_axis_tile_vertices: list[Coordinate] = cubic_tile_to_vertices(
            shifted_on_x_axis_tile, lc
        )
        assert len(shifted_on_x_axis_tile_vertices) == 4
        assert shifted_on_x_axis_tile_vertices[0] == Coordinate(5, 0, 1)  # F
        assert shifted_on_x_axis_tile_vertices[1] == Coordinate(5, 0, 0)  # B
        assert shifted_on_x_axis_tile_vertices[2] == Coordinate(4, 0, 0)  # C
        assert shifted_on_x_axis_tile_vertices[3] == Coordinate(4, 0, 1)  # G

        shifted_on_xy_plane = Tile(Coordinate(7, 0, -2, TileCubicPlacement.BOTTOM))
        shifted_on_xy_plane_vertices: list[Coordinate] = cubic_tile_to_vertices(
            shifted_on_xy_plane, lc
        )
        assert len(shifted_on_xy_plane_vertices) == 4
        assert shifted_on_xy_plane_vertices[0] == Coordinate(8, 0, -1)  # F
        assert shifted_on_xy_plane_vertices[1] == Coordinate(8, 0, -2)  # B
        assert shifted_on_xy_plane_vertices[2] == Coordinate(7, 0, -2)  # C
        assert shifted_on_xy_plane_vertices[3] == Coordinate(7, 0, -1)  # G

    def test_construct_landscape_mesh(self, linear_landscape_strip: Landscape) -> None:
        assert len(linear_landscape_strip.tiles) == 6
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)

        for tile in linear_landscape_strip.tiles.values():
            tile_vertices = cubic_tile_to_vertices(
                tile, linear_landscape_strip.characteristics
            )
            mesh.add_polygon(tile_vertices)

        # The general mesh stats.
        assert mesh.num_vertices() == 14
        assert mesh.num_faces() == 6
        assert mesh.num_edges() == 19

    def test_deep_clone_mesh(self, linear_landscape_strip: Landscape) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)

        for tile in linear_landscape_strip.tiles.values():
            tile_vertices = cubic_tile_to_vertices(
                tile, linear_landscape_strip.characteristics
            )
            mesh.add_polygon(tile_vertices)

        mesh_clone: MeshLike = mesh.deep_copy()

        # The general mesh stats should be the same.
        assert mesh_clone.num_vertices() == mesh.num_vertices()
        assert mesh_clone.num_faces() == mesh.num_faces()
        assert mesh_clone.num_edges() == mesh.num_edges()

        # The memory locations should be different for faces, vertices, and half-edges.
        for face_index in range(mesh.num_faces()):
            assert (
                mesh.faces[face_index].face_id == mesh_clone.faces[face_index].face_id
            )
            assert id(mesh.faces[face_index]) != id(mesh_clone.faces[face_index])

        cloned_edge: MeshHalfEdgeLike
        for cloned_edge in mesh_clone.edges:
            # The edge exists in both meshes.
            original_edge = mesh.edge(cloned_edge.edge_id)

            assert original_edge is not None
            assert cloned_edge.edge_id == original_edge.edge_id
            assert cloned_edge.face_id == original_edge.face_id
            assert cloned_edge.origin_vertex_id == original_edge.origin_vertex_id

            # The edge has a different memory address.
            assert id(original_edge) != id(cloned_edge)

        cloned_vertex: MeshVertexLike
        for cloned_vertex in mesh_clone.vertices:
            # The vertex exists in both meshes.
            original_vertex = mesh.vertex(cloned_vertex.vertex_id)
            assert cloned_vertex.vertex_id == original_vertex.vertex_id
            assert cloned_vertex.vertex_indicator == original_vertex.vertex_indicator
            assert cloned_vertex.edge_id == original_vertex.edge_id
            assert id(cloned_vertex) != id(original_vertex)

    def test_problematic_deep_clone(
        self, plane_with_changing_y_value: Landscape
    ) -> None:
        # The associated mesh originally could not be cloned using an reference based
        # implementation of the half-edge data structure.
        # Switching to a lookup based half-edge implementation corrects the issue.
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)

        for tile in plane_with_changing_y_value.tiles.values():
            tile_vertices = cubic_tile_to_vertices(
                tile, plane_with_changing_y_value.characteristics
            )
            mesh.add_polygon(tile_vertices)

        mesh_clone: MeshLike = mesh.deep_copy()

        assert mesh_clone.num_vertices() == mesh.num_vertices()
        assert mesh_clone.num_faces() == mesh.num_faces()
        assert mesh_clone.num_edges() == mesh.num_edges()

    def test_single_2d_polygon_general_stats(self, polygon_a: list[Coordinate]) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)

        # The general mesh stats.
        assert mesh.num_vertices() == 4
        assert mesh.num_faces() == 1
        assert mesh.num_edges() == 4

        assert mesh.faces[0].count_boundary_edges(mesh) == 4

    def test_single_2d_polygon_verts(self, polygon_a: list[Coordinate]) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)

        # All the vertices are in the mesh.
        for coordinate in polygon_a:
            assert mesh.vertex_at(coordinate) is not None

    def test_single_2d_polygon_first_vertex(self, polygon_a: list[Coordinate]) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)

        # Inspect the first vertex.
        v1 = mesh.vertex_at(Coordinate(2, 3))
        assert v1.location == Coordinate(2, 3)

        edge = v1.edge(mesh)
        assert edge.edge_indicator == 1
        assert edge.edge_id == hash(((2, 3), (6, 6)))
        assert edge.face_id is not None

        pair_edge = edge.pair_edge(mesh)
        assert pair_edge is not None
        assert pair_edge.edge_id == hash(((6, 6), (2, 3)))
        assert pair_edge.face_id == UNSET_MESH_ID

        origin_vertex = pair_edge.origin_vertex(mesh)
        assert origin_vertex is not None
        assert origin_vertex.location == Coordinate(6, 6)

    def test_single_2d_polygon_second_vertex(self, polygon_a: list[Coordinate]) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)

        # Inspect the second vertex.
        v2 = mesh.vertex_at(Coordinate(6, 6))
        assert v2.location == Coordinate(6, 6)
        edge = v2.edge(mesh)
        assert edge.edge_indicator == 2
        assert edge.edge_id == hash(((6, 6), (9, 3)))
        assert edge.face_id != UNSET_MESH_ID
        pair_edge = edge.pair_edge(mesh)
        assert pair_edge is not None
        assert pair_edge.edge_id == hash(((9, 3), (6, 6)))
        assert pair_edge.face_id == UNSET_MESH_ID
        assert pair_edge.origin_vertex(mesh).location == Coordinate(9, 3)  # type:ignore

    def test_single_2d_polygon_third_vertex(self, polygon_a: list[Coordinate]) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)
        # Inspect the third vertex.
        v3 = mesh.vertex_at(Coordinate(9, 3))
        assert v3.location == Coordinate(9, 3)
        edge = v3.edge(mesh)
        assert edge.edge_indicator == 3
        assert edge.edge_id == hash(((9, 3), (5, 1)))
        assert edge.face_id is not None

        pair_edge = edge.pair_edge(mesh)
        assert pair_edge is not None
        assert pair_edge.edge_id == hash(((5, 1), (9, 3)))
        assert pair_edge.face_id == UNSET_MESH_ID

        origin_vertex = pair_edge.origin_vertex(mesh)
        assert origin_vertex is not None
        assert origin_vertex.location == Coordinate(5, 1)

    def test_single_2d_polygon_fourth_vertex(self, polygon_a: list[Coordinate]) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)

        # Inspect the fourth vertex.
        v4 = mesh.vertex_at(Coordinate(5, 1))
        assert v4.location == Coordinate(5, 1)

        edge = v4.edge(mesh)
        assert edge.edge_indicator == 4
        assert edge.edge_id == hash(((5, 1), (2, 3)))
        assert edge.face_id is not None

        pair_edge = edge.pair_edge(mesh)
        assert pair_edge is not None
        assert pair_edge.edge_id == hash(((2, 3), (5, 1)))
        assert pair_edge.face_id == UNSET_MESH_ID

        origin_vertex = pair_edge.origin_vertex(mesh)
        assert origin_vertex is not None
        assert origin_vertex.location == Coordinate(2, 3)

    def test_two_connected_2d_polygon_stats(
        self, polygon_a: list[Coordinate], polygon_b: list[Coordinate]
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)
        mesh.add_polygon(polygon_b)
        assert mesh.num_vertices() == 6
        assert mesh.num_faces() == 2
        assert mesh.num_edges() == 7

    def test_two_connected_2d_polygon_verts(
        self, polygon_a: list[Coordinate], polygon_b: list[Coordinate]
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)
        mesh.add_polygon(polygon_b)
        # All the vertices are in the mesh.
        for coordinate in polygon_a + polygon_b:
            assert mesh.vertex_at(coordinate) is not None

    def test_two_connected_2d_polygon_existing_edges(
        self, polygon_a: list[Coordinate], polygon_b: list[Coordinate]
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)
        mesh.add_polygon(polygon_b)

        # Inspect the edge between vertices 2 and 3.
        # Adding the second polygon should have set the face on
        # the external edge between vert 2 and 3 to Face ID #2.
        # It's twin should be associated with Face ID #1.
        half_edge_between_verts_2_3 = mesh.half_edge_between(
            Coordinate(9, 3), Coordinate(6, 6)
        )
        assert half_edge_between_verts_2_3 is not None
        assert half_edge_between_verts_2_3.edge_indicator == 2
        assert half_edge_between_verts_2_3.face_id == 2
        pair_edge = half_edge_between_verts_2_3.pair_edge(mesh)
        assert pair_edge is not None
        assert pair_edge.face_id == 1

    def test_inner_boundary_connectivity_face_1(
        self, polygon_a: list[Coordinate], polygon_b: list[Coordinate]
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)
        mesh.add_polygon(polygon_b)

        # Verify that the face ID is the same as the dict key.
        face_1: MeshFaceLike = mesh._faces[1]
        assert face_1.face_id == 1

        # Verify that the inner half-edges are correct for Face 1.
        first_edge = face_1.boundary_edge(mesh)
        assert first_edge.edge_indicator == 1
        assert first_edge.edge_id == hash(((2, 3), (6, 6)))

        next_edge = first_edge.next_edge(mesh)
        assert next_edge.edge_indicator == 2
        assert next_edge.edge_id == hash(((6, 6), (9, 3)))

        third_edge = next_edge.next_edge(mesh)
        assert third_edge.edge_indicator == 3
        assert third_edge.edge_id == hash(((9, 3), (5, 1)))

        fourth_edge = third_edge.next_edge(mesh)
        assert fourth_edge.edge_indicator == 4
        assert fourth_edge.edge_id == hash(((5, 1), (2, 3)))

    def test_inner_boundary_connectivity_face_2(
        self, polygon_a: list[Coordinate], polygon_b: list[Coordinate]
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)
        mesh.add_polygon(polygon_b)

        # Verify that the face ID is the same as the dict key.
        face_2: MeshFaceLike = mesh._faces[2]
        assert face_2.face_id == 2

        # Verify that the inner half-edges are correct for Face 2.
        assert face_2.boundary_edge(mesh).edge_indicator == 2
        assert face_2.boundary_edge_id == hash(((9, 3), (6, 6)))

        next_edge = face_2.boundary_edge(mesh).next_edge(mesh)
        assert next_edge is not None
        assert next_edge.edge_indicator == 5
        assert next_edge.edge_id == hash(((6, 6), (10, 7)))

        third_edge = next_edge.next_edge(mesh)
        assert third_edge is not None
        assert third_edge.edge_indicator == 6
        assert third_edge.edge_id == hash(((10, 7), (13, 4)))

        fourth_edge = third_edge.next_edge(mesh)
        assert fourth_edge is not None
        assert fourth_edge.edge_indicator == 7
        assert fourth_edge.edge_id == hash(((13, 4), (9, 3)))

    def test_outer_boundary_connectivity_for_single_face(
        self, polygon_a: list[Coordinate]
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)

        face_1: MeshFaceLike = mesh._faces[1]
        boundary_edge = face_1.boundary_edge(mesh)
        assert boundary_edge is not None

        starting_outer_edge = boundary_edge.pair_edge(mesh)
        assert starting_outer_edge is not None
        assert starting_outer_edge.edge_indicator == 1
        assert starting_outer_edge.edge_id == hash(((6, 6), (2, 3)))
        assert starting_outer_edge.face_id == UNSET_MESH_ID

        # There should 4 outer edges and all outer edges should not have an associated face.
        # The outer boundary should be:
        # Edge 1 -> Edge 4 -> Edge 3 -> Edge 2
        edge_visit_order = []
        collect_edge_indicators = lambda e: edge_visit_order.append(e.edge_indicator)

        edge_counter = CounterBuilder.count_up_from_zero()
        traverse_edges_by_next(
            mesh,
            starting_outer_edge,
            max_traversals=10,
            actions=[assert_edge_with_no_face, collect_edge_indicators],
            counter=edge_counter,
        )
        assert edge_counter.value() == 4
        assert edge_visit_order == [1, 4, 3, 2]

    def test_traversing_around_vertices_for_single_face(
        self, polygon_a: list[Coordinate]
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)

        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(2, 3),
            expected_num_edges=2,
            expected_edge_order=[1, 4],
        )  # V1
        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(6, 6),
            expected_num_edges=2,
            expected_edge_order=[2, 1],
        )  # V2
        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(9, 3),
            expected_num_edges=2,
            expected_edge_order=[3, 2],
        )  # V3
        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(5, 1),
            expected_num_edges=2,
            expected_edge_order=[4, 3],
        )  # V4

    def test_traversing_around_vertices_for_two_faces(
        self, polygon_a: list[Coordinate], polygon_b: list[Coordinate]
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)
        mesh.add_polygon(polygon_b)

        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(2, 3),
            expected_num_edges=2,
            expected_edge_order=[1, 4],
        )  # V1
        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(6, 6),
            expected_num_edges=3,
            expected_edge_order=[2, 5, 1],
        )  # V2
        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(9, 3),
            expected_num_edges=3,
            expected_edge_order=[3, 7, 2],
        )  # V3
        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(5, 1),
            expected_num_edges=2,
            expected_edge_order=[4, 3],
        )  # V4
        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(10, 7),
            expected_num_edges=2,
            expected_edge_order=[6, 5],
        )  # V5
        verify_vertex_edges(
            mesh,
            vertex_at=Coordinate(13, 4),
            expected_num_edges=2,
            expected_edge_order=[7, 6],
        )  # V6

    def test_outer_boundary_connectivity_for_two_faces(
        self, polygon_a: list[Coordinate], polygon_b: list[Coordinate]
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)
        mesh.add_polygon(polygon_b)

        face_1: MeshFaceLike = mesh._faces[1]
        starting_outer_edge: MeshHalfEdge = face_1.boundary_edge(mesh).pair_edge(mesh)  # type: ignore
        assert starting_outer_edge.edge_indicator == 1
        assert starting_outer_edge.edge_id == hash(((6, 6), (2, 3)))
        assert starting_outer_edge.face_id == UNSET_MESH_ID

        # There should 6 outer edges and all outer edges should not have an associated face.
        # The outer boundary should be:
        # Edge 1 -> Edge 4 -> Edge 3 -> Edge 7 -> Edge 6 -> Edge 5
        edge_visit_order = []
        collect_edge_indicators = lambda e: edge_visit_order.append(e.edge_indicator)

        edge_counter = CounterBuilder.count_up_from_zero()
        traverse_edges_by_next(
            mesh,
            starting_outer_edge,
            max_traversals=10,
            actions=[assert_edge_with_no_face, collect_edge_indicators],
            counter=edge_counter,
        )
        assert edge_counter.value() == 6
        assert edge_visit_order == [1, 4, 3, 7, 6, 5]

    def test_traverse_faces_around_vertex(
        self,
        polygon_a: list[Coordinate],
        polygon_b: list[Coordinate],
        polygon_c: list[Coordinate],
    ) -> None:
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        mesh.add_polygon(polygon_a)
        mesh.add_polygon(polygon_b)
        mesh.add_polygon(polygon_c)

        face_ids: list[int] = []
        collect_face_ids = lambda face: face_ids.append(face.face_id)
        actions = [collect_face_ids]
        vert = mesh.vertex_at(Coordinate(9, 3))  # Vertex 3
        num_faces = vert.traverse_faces(mesh, actions)

        assert num_faces == 3
        assert face_ids == [1, 3, 2]

        face_ids.clear()
        vert = mesh.vertex_at(Coordinate(5, 1))  # Vertex 4
        num_faces = vert.traverse_faces(mesh, actions)
        assert num_faces == 1
        assert face_ids == [1]

        face_ids.clear()
        vert = mesh.vertex_at(Coordinate(13, 4))  # Vertex 6
        num_faces = vert.traverse_faces(mesh, actions)
        assert num_faces == 2
        assert face_ids == [2, 3]

    def test_3d_cube_stats(self, landscape_cube: Landscape) -> None:
        """Construct a half-edge mesh with all sides of a cube."""
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)

        for tile in landscape_cube.tiles.values():
            tile_vertices = cubic_tile_to_vertices(tile, landscape_cube.characteristics)
            mesh.add_polygon(tile_vertices)

        assert mesh.num_vertices() == 8
        assert mesh.num_faces() == 6
        assert mesh.num_edges() == 12

    def test_3d_cube_faces(self, landscape_cube: Landscape) -> None:
        """Construct a half-edge mesh with all sides of a cube."""
        mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CCW)
        table_printer = MeshTablePrinter()

        for tile in landscape_cube.tiles.values():
            tile_vertices = cubic_tile_to_vertices(tile, landscape_cube.characteristics)
            mesh.add_polygon(tile_vertices)

        table_printer.print(mesh)

        # Face 1: On the bottom.
        assert len(mesh.faces[0].vertices(mesh)) == 4
        num_edges = mesh.faces[0].traverse_edges(mesh, [])
        assert num_edges == 4

        # assert False
        # Face 2:
        assert len(mesh.faces[1].vertices(mesh)) == 4
        num_edges = mesh.faces[1].traverse_edges(mesh, [])
        assert num_edges == 4

    def test_load_skull(self) -> None:
        scene_dir = "poc/pyside_webgpu/pyside_webgpu/demos/obj/models"
        scene_filename = "skull.obj"
        path = os.path.join(Path.cwd(), scene_dir, scene_filename)
        obj = ObjLoader().load(path)
        mesh = obj_to_mesh(obj)


def traverse_edges_by_next(
    mesh: MeshLike,
    starting_edge: MeshHalfEdgeLike,
    max_traversals: int,
    actions: list[Callable[[MeshHalfEdgeLike], None]],
    counter: Counter,
) -> None:
    """Given a half-edge, follows the next points until a loop is encountered."""
    first_edge: MeshHalfEdgeLike = starting_edge
    current_edge: MeshHalfEdgeLike | None = starting_edge
    while True:
        counter.increment()
        for action in actions:
            action(current_edge)
        current_edge = current_edge.next_edge(mesh)
        if (
            current_edge is None
            or current_edge == first_edge
            or counter.value() > max_traversals
        ):
            break


def assert_edge_with_no_face(edge: MeshHalfEdgeLike):
    assert edge.face_id == UNSET_MESH_ID


# TODO: Move this to be on MeshVertex
def traverse_edges_around_vertex(
    mesh: MeshLike,
    vertex: MeshVertexLike,
    max_traversals: int,
    actions: list[Callable[[MeshHalfEdgeLike], None]],
    counter: Counter,
) -> None:
    """Given a mesh vertex, visit all of the edges that start from the vertex."""
    if vertex.edge_id is None:
        raise MeshException(
            "Cannot traverse around a vertex that has no associated edge"
        )

    starting_edge: MeshHalfEdgeLike = vertex.edge(mesh)
    current_edge: MeshHalfEdgeLike = starting_edge

    while True:
        counter.increment()
        for action in actions:
            action(current_edge)

        if current_edge.pair_edge_id == UNSET_MESH_ID:
            # Stop if the current edge has no twin.
            # Note: This shouldn't happen. Perhaps change this to throw an exception.
            break

        pair_edge = current_edge.pair_edge(mesh)
        if pair_edge.next_edge_id == UNSET_MESH_ID:
            # Stop if the paired edge don't have a next edge.
            # This shouldn't happen. Perhaps change this to throw an exception.
            break

        # Shift to the next edge on the vertex.
        current_edge = pair_edge.next_edge(mesh)

        if current_edge == starting_edge:
            # Stop if we're back where we started.
            break

        if counter.value() > max_traversals:
            # Stop if we've been doing this for two long.
            break


def verify_vertex_edges(
    mesh: MeshLike,
    vertex_at: Coordinate,
    expected_num_edges: int,
    expected_edge_order: list[int],
    max_traversals=10,
) -> None:
    edge_order = []
    collect_outbound_edges = lambda e: edge_order.append(e.edge_indicator)
    edge_counter = CounterBuilder.count_up_from_zero()

    vertex = mesh.vertex_at(vertex_at)
    traverse_edges_around_vertex(
        mesh,
        vertex=vertex,
        max_traversals=max_traversals,
        actions=[collect_outbound_edges],
        counter=edge_counter,
    )
    assert (
        edge_counter.value() == expected_num_edges
    ), f"The vertex {vertex.location} did not have the expected number of edges."
    assert (
        edge_order == expected_edge_order
    ), "The traversal order was not what was expected."
