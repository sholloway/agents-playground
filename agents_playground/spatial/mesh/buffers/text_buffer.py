from math import ceil

import wgpu

from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import MeshBuffer, MeshBufferError
from agents_playground.spatial.vector.vector import Vector


class TextBuffer(MeshBuffer):
    """
    An implementation of MeshBuffer designed for working with the TextRenderer.
    """

    def __init__(self) -> None:
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
        pass
