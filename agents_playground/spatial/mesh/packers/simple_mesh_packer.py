from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import (
    MeshBuffer,
    MeshFaceLike,
    MeshLike,
    MeshPacker,
    MeshVertexLike,
)
from agents_playground.spatial.mesh.buffers.triangle_mesh_buffer import (
    TriangleMeshBuffer,
)
from agents_playground.spatial.mesh.half_edge_mesh import MeshException

# The Barycentric coordinates for the triangle's three vertices.
A = Coordinate(1.0, 0.0, 0.0)
B = Coordinate(0.0, 1.0, 0.0)
C = Coordinate(0.0, 0.0, 1.0)


def assign_bc_coordinate(vert_index: int) -> Coordinate:
    match vert_index:
        case 0:
            return A
        case 1:
            return B
        case 2:
            return C
        case _:
            raise MeshException(f"The vertex index {vert_index} was unexpected.")


class SimpleMeshPacker(MeshPacker):
    """
    Given a half-edge mesh composed of triangles, packs a MeshBuffer in the order:
    Vx, Vy, Vz, Vw, Tu, Tv, Tw, Ni, Nj, Nk, Ba, Bb, Bc

    Where:
    - A vertex in 3D space is defined by Vx, Vy, Vz.
    - The related texture coordinates (stubbed to 0 for now) is defined by Tu, Tv, Tw.
    - The vertex normal is defined by Ni, Nj, Nk.
    - The Barycentric coordinate of the vertex is defined by Ba, Bb, Bc.
    """

    def pack(self, mesh: MeshLike) -> MeshBuffer:
        """Given a mesh, packs it into a MeshBuffer."""
        buffer: MeshBuffer = TriangleMeshBuffer()

        # Just pack the vertices and normals together to enable quickly rendering.
        face: MeshFaceLike
        fake_texture_coord = Coordinate(0.0, 0.0, 0.0)

        for face in mesh.faces:
            vertices: tuple[MeshVertexLike, ...] = face.vertices(mesh)
            for index, vertex in enumerate(vertices):
                bc = assign_bc_coordinate(index)
                match vertex.location.dimensions():
                    case 3:
                        buffer.pack_vertex(
                            location=Coordinate(
                                *vertex.location, 1.0
                            ),  # Add a W component to the vertex location.
                            texture=fake_texture_coord,
                            normal=vertex.normal,  # type: ignore
                            bc_coord=bc,
                        )
                    case 4:
                        buffer.pack_vertex(
                            location=vertex.location,
                            texture=fake_texture_coord,
                            normal=vertex.normal,  # type: ignore
                            bc_coord=bc,
                        )
                    case _:
                        raise MeshException(
                            f"Unexpected number of dimensions.\nExpected 3 or 4 but {vertex.location.dimensions()} was encountered."
                        )
        return buffer
