from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import MeshBuffer
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
    self._data: list[float] = [] # Vertex Buffer Object (VBO)
    self._index: list[int] = []  # Vertex Index Buffer (VIO), starting at 0.
    self._vertex_counter: Counter[int] = CounterBuilder.count_up_from_zero()
    
  def pack_vertex(
    self, 
    location: Coordinate, 
    texture: Coordinate, 
    normal: Vector,
    bc_coord: Coordinate
  ) -> None:
    self._data.extend(
      (
        *location.to_tuple(), 
        *texture.to_tuple(), 
        *normal.to_tuple(), 
        *bc_coord.to_tuple()
      )
    )
    self._index.append(self._vertex_counter.value())
    self._vertex_counter.increment()

  @property
  def vertices(self) -> list[float]:
    return self._data
  
  @property
  def vertex_normals(self) -> list[float]:
    raise NotImplemented()
  
  @property
  def vertex_index(self) -> list[int]:
    return self._index
 
  @property
  def normal_index(self) -> list[int]:
    raise NotImplemented()
  
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
    buffer_size = len(self._data)
    num_verts = buffer_size/offset
    table_format = "{:<30} {:<30} {:<30} {:<30}"
    header = table_format.format('Vertex', 'Texture', 'Normal', 'BC')
    print(header)
    for row in range(round(num_verts)):
      row_offset = row * offset
      position_x = self._data[row_offset + 0]
      position_y = self._data[row_offset + 1]
      position_z = self._data[row_offset + 2]
      position_w = self._data[row_offset + 3]
      position = f'V({position_x},{position_y},{position_z},{position_w})'

      texture_a = self._data[row_offset + 4]
      texture_b = self._data[row_offset + 5]
      texture = f'T({texture_a}, {texture_b})'

      normal_i = self._data[row_offset + 6]
      normal_j = self._data[row_offset + 7]
      normal_k = self._data[row_offset + 8]
      normal = f'N({normal_i},{normal_j},{normal_k})'

      bc_a = self._data[row_offset + 9]
      bc_b = self._data[row_offset + 10]
      bc_c = self._data[row_offset + 11]
      bc = f'bc({bc_a},{bc_b},{bc_c})'

      row_str = table_format.format(position, texture, normal, bc)
      print(row_str)