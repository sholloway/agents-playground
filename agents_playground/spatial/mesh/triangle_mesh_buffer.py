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