from abc import abstractmethod
from typing import Protocol

class MeshBuffer(Protocol):
  """
  A mesh buffer is a collection of vertices, vertex normals and an index that are arranged
  to be passed to a GPU rendering pipeline for rendering.
  """
  @property
  @abstractmethod
  def vertices(self) -> list[float]:
    ...
  
  @property
  @abstractmethod
  def vertex_normals(self) -> list[float]:
    ...
  
  @property
  @abstractmethod
  def vertex_index(self) -> list[int]:
    ...
 
  @property
  @abstractmethod
  def normal_index(self) -> list[int]:
    ...