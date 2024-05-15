from math import ceil

import wgpu

from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import MeshBuffer, MeshBufferError
from agents_playground.spatial.vector.vector import Vector


class TriangleMeshBuffer(MeshBuffer):
    """
    Implements the MeshBuffer protocol for triangles.
    """

    def __init__(self) -> None:
        """
        Create a new mesh buffer filled with the data required to render triangles.

        ### Note
        At the moment just packing verts and normals together to reuse shaders and pipeline.

        ### The Packing Format
        The shader at the moment is at poc/pyside_webgpu/demos/obj/shaders/triangle.wgsl.
        It expects a vertex input of the below structure.

        A triangle is composed of 3 vertices. Each vertex has the following data:
        struct VertexInput {
          @location(0) position: vec4<f32>,
          @location(1) texture: vec2<f32>,
          @location(2) normal: vec3<f32>,
          @location(3) barycentric: vec3<f32>
        };

        These needed to be packed in the self._data list per vertex like so:
          (position, texture coordinates, normal, barycentric coordinates)

        Example:
        self._data.extend((*v1_pos, *v1_tex, *v1_norm, *bc_coords))
        """
        self._data: list[float] = []  # Vertex Buffer Object (VBO)
        self._index: list[int] = []  # Vertex Index Buffer (VIO), starting at 0.
        self._vertex_counter: Counter[int] = CounterBuilder.count_up_from_zero()
        self._vbo: Maybe[wgpu.GPUBuffer] = Nothing()
        self._ibo: Maybe[wgpu.GPUBuffer] = Nothing()
        self._bind_groups: dict[int, wgpu.GPUBindGroup] = {}

    @property
    def count(self) -> int:
        """Returns the number of items (e.g. vertices are in the buffer.)"""
        return self._vertex_counter.value()

    def pack_vertex(
        self,
        location: Coordinate,
        texture: Coordinate,
        normal: Vector,
        bc_coord: Coordinate,
    ) -> None:
        self._data.extend(
            (
                *location.to_tuple(),
                *texture.to_tuple(),
                *normal.to_tuple(),
                *bc_coord.to_tuple(),
            )
        )
        self._index.append(self._vertex_counter.value())
        self._vertex_counter.increment()

    @property
    def data(self) -> list[float]:
        return self._data

    @property
    def index(self) -> list[int]:
        return self._index

    @property
    def vbo(self) -> wgpu.GPUBuffer:
        if not self._vbo.is_something():
            raise MeshBufferError(
                "Attempted to access an unset VBO on a TriangleMeshBuffer."
            )
        return self._vbo.unwrap()

    @vbo.setter
    def vbo(self, buffer: wgpu.GPUBuffer) -> None:
        self._vbo = Something(buffer)

    @property
    def ibo(self) -> wgpu.GPUBuffer:
        if not self._ibo.is_something():
            raise MeshBufferError(
                "Attempted to access an unset IBO on a TriangleMeshBuffer."
            )
        return self._ibo.unwrap()

    @ibo.setter
    def ibo(self, buffer: wgpu.GPUBuffer) -> None:
        self._ibo = Something(buffer)

    @property
    def bind_groups(self) -> dict[int, wgpu.GPUBindGroup]:
        """Returns a dictionary that maps the mesh's bind groups to their group positions."""
        return self._bind_groups

    def print(self) -> None:
        """
        Writing the contents of the mesh buffer to STDOUT.
        """
        # Need to iterate over the _data list in chunks based the packing of the data buffer.
        # (position, texture coordinates, normal, barycentric coordinates)
        # (4,        3,                   3,      3)

        # 1. Determine the offset/stride of the packed data.
        offset = 4 + 3 + 3 + 3
        buffer_size = len(self._data)
        num_verts = buffer_size / offset

        # 2. Loop over the buffer to build up the row of strings.
        # Find the maximum required width of each column.
        max_vert_col = max_tex_col = max_norm_col = max_bc_col = 0
        table_rows: list[tuple[str, ...]] = []
        for row in range(ceil(num_verts)):
            row_offset = row * offset
            position_x = self._data[row_offset + 0]
            position_y = self._data[row_offset + 1]
            position_z = self._data[row_offset + 2]
            position_w = self._data[row_offset + 3]
            position_field = (
                f"V({position_x}, {position_y}, {position_z}, {position_w})"
            )
            max_vert_col = max(max_vert_col, len(position_field))

            texture_a = self._data[row_offset + 4]
            texture_b = self._data[row_offset + 5]
            texture_c = self._data[row_offset + 6]
            texture_field = f"T({texture_a}, {texture_b}, {texture_c})"
            max_tex_col = max(max_tex_col, len(texture_field))

            normal_i = self._data[row_offset + 7]
            normal_j = self._data[row_offset + 8]
            normal_k = self._data[row_offset + 9]
            normal_field = f"N({normal_i}, {normal_j}, {normal_k})"
            max_norm_col = max(max_norm_col, len(normal_field))

            bc_a = self._data[row_offset + 10]
            bc_b = self._data[row_offset + 11]
            bc_c = self._data[row_offset + 12]
            bc_field = f"bc({bc_a}, {bc_b}, {bc_c})"
            max_bc_col = max(max_bc_col, len(bc_field))

            table_rows.append((position_field, texture_field, normal_field, bc_field))

        # 3. Print the table to STDOUT.
        table_format = (
            "{:<"
            + str(max_vert_col)
            + "}     {:<"
            + str(max_vert_col)
            + "}     {:<"
            + str(max_norm_col)
            + "}     {:<"
            + str(max_bc_col)
            + "}"
        )
        table_width = max_vert_col + max_vert_col + max_norm_col + max_bc_col + 5 * 3
        header = table_format.format("Vertex", "Texture", "Normal", "BC")
        print(header)
        print("-" * table_width)
        for row in table_rows:
            row_str = table_format.format(row[0], row[1], row[2], row[3])
            print(row_str)
