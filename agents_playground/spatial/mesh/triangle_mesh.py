from __future__ import annotations

from agents_playground.loaders.obj_loader import Obj


class TriangleMesh:
    """
    Groups the various lists that must be created to load a mesh of triangles
    into GPUBuffer instances.
    """

    def __init__(self) -> None:
        self.data: list[float] = []
        self.index: list[int] = []

    @property
    def vertex_index(self) -> list[int]:
        return self.index

    @staticmethod
    def from_obj(obj: Obj) -> TriangleMesh:
        """
        Given an Obj instance, produce a list of triangles defined by their vertices.

        A mesh is a collection of triangles. Each triangle is composed of 3 vertices.
        Each vertex has a normal, texture coordinate, and Barycentric Coordinate.

        An index is provided to specify the vertex order.
        An index buffer must be used to render the mesh.
        Each stride in the VBO is of the form:
        Vx, Vy, Vz, Vw, Tu, Tv, Ni, Nj, Nk, Ba, Bb, Bc
        """
        # Question: How does the stride impact the index buffer?
        mesh = TriangleMesh()
        vertex_count = 0

        # The Barycentric coordinates for the triangle's three vertices.
        a = (1.0, 0.0, 0.0)
        b = (0.0, 1.0, 0.0)
        c = (0.0, 0.0, 1.0)

        # Step 3: Build an index buffer that provides the order in which the vertices
        # and their normals should be accessed to construct the polygons.
        for polygon in obj.polygons:
            # Build either a single triangle (3 verts) or a fan (>3 verts) of triangles.
            # Note: The OBJ file format store vertices in CCW order. That is maintained here.

            v1_pos = obj.vertices[polygon.vertices[0].vertex - 1]
            v1_tex = (
                obj.texture_coordinates[polygon.vertices[0].texture - 1]
                if polygon.vertices[0].texture is not None
                else (0, 0)
            )
            v1_norm = (
                obj.vertex_normals[polygon.vertices[0].normal - 1]
                if polygon.vertices[0].normal is not None
                else (0, 0, 0)
            )

            for vert_index in range(1, len(polygon.vertices) - 1):
                # Build triangles using the fan point and the other vertices.
                v2_index = polygon.vertices[vert_index]
                v3_index = polygon.vertices[vert_index + 1]

                # Add the triangle point. This will be added multiple times for a fan.
                mesh.data.extend((*v1_pos, *v1_tex, *v1_norm, *a))
                mesh.index.append(vertex_count)
                vertex_count += 1

                v2_pos = obj.vertices[v2_index.vertex - 1]
                v2_tex = (
                    obj.texture_coordinates[v2_index.texture - 1]
                    if v2_index.texture is not None
                    else (0, 0)
                )
                v2_norm = (
                    obj.vertex_normals[v2_index.normal - 1]
                    if v2_index.normal is not None
                    else (0, 0, 0)
                )

                mesh.data.extend((*v2_pos, *v2_tex, *v2_norm, *b))
                mesh.index.append(vertex_count)
                vertex_count += 1

                v3_pos = obj.vertices[v3_index.vertex - 1]
                v3_tex = (
                    obj.texture_coordinates[v3_index.texture - 1]
                    if v3_index.texture is not None
                    else (0, 0, 0)
                )
                v3_norm = (
                    obj.vertex_normals[v3_index.normal - 1]
                    if v3_index.normal is not None
                    else (0, 0, 0)
                )

                mesh.data.extend((*v3_pos, *v3_tex, *v3_norm, *c))
                mesh.index.append(vertex_count)
                vertex_count += 1

        return mesh

    def print(self) -> None:
        """
        Writing the contents of the mesh buffer to STDOUT.
        """
        # Need to iterate over the _data list in chunks based the packing of the
        # data buffer.
        # (position, texture coordinates, normal, barycentric coordinates)
        # (3,        2,                   3,      3)
        # 11
        offset = 4 + 2 + 3 + 3
        buffer_size = len(self.data)
        num_verts = buffer_size / offset
        table_format = "{:<40} {:<30} {:<40} {:<40}"
        header = table_format.format("Vertex", "Texture", "Normal", "BC")
        print(header)
        for row in range(round(num_verts)):
            row_offset = row * offset
            position_x = self.data[row_offset + 0]
            position_y = self.data[row_offset + 1]
            position_z = self.data[row_offset + 2]
            position_w = self.data[row_offset + 3]
            position = f"V({position_x},{position_y},{position_z}, {position_w})"

            texture_a = self.data[row_offset + 4]
            texture_b = self.data[row_offset + 5]
            texture = f"T({texture_a}, {texture_b})"

            normal_i = self.data[row_offset + 6]
            normal_j = self.data[row_offset + 7]
            normal_k = self.data[row_offset + 8]
            normal = f"N({normal_i},{normal_j},{normal_k})"

            bc_a = self.data[row_offset + 9]
            bc_b = self.data[row_offset + 10]
            bc_c = self.data[row_offset + 11]
            bc = f"bc({bc_a},{bc_b},{bc_c})"

            row_str = table_format.format(position, texture, normal, bc)
            print(row_str)
