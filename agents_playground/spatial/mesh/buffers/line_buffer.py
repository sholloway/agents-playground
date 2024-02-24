
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import MeshBuffer


class VertexBuffer(MeshBuffer):
  """
  Implements the MeshBuffer protocol for only vertices.
  This can be used to drive primitives for points, lines, and lines strips.
  """
  def __init__(self) -> None:
    self._data: list[float] = [] # Vertex Buffer Object (VBO)
    self._index: list[int] = []  # Vertex Index Buffer (VIO), starting at 0.
    self._vertex_counter: Counter[int] = CounterBuilder.count_up_from_zero()

  @property
  def data(self) -> list[float]:
    return self._data
  
  @property
  def index(self) -> list[int]:
    return self._index
  
  @property
  def count(self) -> int:
    """Returns the number of items (e.g. vertices are in the buffer.)"""
    return self._vertex_counter.value()
  
  def pack(self, v: Coordinate) -> None:
    """
    Given a coordinate, V pack it in the order:
    Vx, Vy, Vz
    """

    # NOTE: I may be thinking about this wrong. I may need to pack the VBO one 
    # vertex at a time. 
    self._data.extend(
      (
        *v.to_tuple(),
      )
    )

    self._index.append(self._vertex_counter.value())
    self._vertex_counter.increment()

  def print(self) -> None:
    raise NotImplementedError()

  