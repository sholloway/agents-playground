
from math import ceil

import wgpu 

from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import MeshBuffer, MeshBufferError

class VertexBuffer(MeshBuffer):
  """
  Implements the MeshBuffer protocol for only vertices.
  This can be used to drive primitives for points, lines, and lines strips.
  """
  def __init__(self) -> None:
    self._data: list[float] = [] # Vertex Buffer Object (VBO)
    self._index: list[int] = []  # Vertex Index Buffer (VIO), starting at 0.
    self._vertex_counter: Counter[int] = CounterBuilder.count_up_from_zero()
    self._vbo: Maybe[wgpu.GPUBuffer] = Nothing()
    self._ibo: Maybe[wgpu.GPUBuffer] = Nothing()
    self._bind_groups: dict[int, wgpu.GPUBindGroup] = {}

  @property
  def data(self) -> list[float]:
    return self._data
  
  @property
  def index(self) -> list[int]:
    return self._index
  
  @property
  def vbo(self) -> wgpu.GPUBuffer:
    if not self._vbo.is_something():
      raise MeshBufferError('Attempted to access an unset VBO on a VertexBuffer.')
    return self._vbo.unwrap()
  
  @vbo.setter
  def vbo(self, buffer: wgpu.GPUBuffer) -> None:
    self._vbo = Something(buffer)
  
  @property
  def ibo(self) -> wgpu.GPUBuffer:
    if not self._ibo.is_something():
      raise MeshBufferError('Attempted to access an unset IBO on a VertexBuffer.')
    return self._ibo.unwrap()

  @ibo.setter
  def ibo(self, buffer: wgpu.GPUBuffer) -> None:
    self._ibo = Something(buffer)

  @property
  def bind_groups(self) -> dict[int, wgpu.GPUBindGroup]:
    """Returns a dictionary that maps the mesh's bind groups to their group positions."""
    return self._bind_groups
  
  @property
  def count(self) -> int:
    """Returns the number of items (e.g. vertices are in the buffer.)"""
    return self._vertex_counter.value()
  
  def pack(self, v: Coordinate) -> None:
    """
    Given a coordinate, V pack it in the order:
    Vx, Vy, Vz, 1
    """

    # NOTE: I may be thinking about this wrong. I may need to pack the VBO one 
    # vertex at a time. 
    self._data.extend(
      (
        *v.to_tuple(),
        1
      )
    )

    self._index.append(self._vertex_counter.value())
    self._vertex_counter.increment()

  def print(self) -> None:
    """
    Writing the contents of the mesh buffer to STDOUT.
    """
    # Need to iterate over the _data list in chunks based the packing of the data buffer.
    # (position (x, y, z, 1))
    # (4)

    # 1. Determine the offset/stride of the packed data.
    offset = 4
    buffer_size = len(self._data)
    num_verts = buffer_size/offset
    print(f'Buffer Size: {buffer_size}, num_verts: {num_verts}')
    
    # 2. Loop over the buffer to build up the row of strings.
    # Find the maximum required width of each column.
    max_vert_col = 0
    table_rows: list[tuple[str, ...]] = []
    for row in range(ceil(num_verts)):
      row_offset = row * offset
      position_x = self._data[row_offset + 0]
      position_y = self._data[row_offset + 1]
      position_z = self._data[row_offset + 2]
      position_field = f'V({position_x}, {position_y}, {position_z})'
      max_vert_col = max(max_vert_col, len(position_field))
      table_rows.append((position_field,))

    # 3. Print the table to STDOUT.
    table_format = "{:<" + str(max_vert_col) +"}"
    table_width = max_vert_col
    header = table_format.format('Vertex')
    print(header)
    print("-"*table_width)
    for row in table_rows:
      row_str = table_format.format(row[0])
      print(row_str)

  