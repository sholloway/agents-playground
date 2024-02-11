from agents_playground.spatial.mesh import MeshBuffer


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
    A triangle is composed of 3 vertices. Each vertex has the following data:
    (position, texture coordinates, normal, barycentric coordinates)
    
    """
    self._data: list[float] = []  
    self._index: list[int] = []

    
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