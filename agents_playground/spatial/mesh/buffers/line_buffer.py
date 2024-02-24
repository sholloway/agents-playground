
from agents_playground.counter.counter import Counter, CounterBuilder
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import MeshBuffer


class LineBuffer(MeshBuffer):
  """
  Implements the MeshBuffer protocol for line primitives.
  """
  def __init__(self) -> None:
    self._data: list[float] = [] # Vertex Buffer Object (VBO)
    self._index: list[int] = []  # Vertex Index Buffer (VIO), starting at 0.
    self._line_counter: Counter[int] = CounterBuilder.count_up_from_zero()

  @property
  def data(self) -> list[float]:
    return self._data
  
  @property
  def index(self) -> list[int]:
    return self._index
  
  def pack_line(self, v: Coordinate, q: Coordinate) -> None:
    """
    Given two coordinates, v and q, pack them in the order:
    Vx, Vy, Vz, Qx, Qy, Qz
    """

    # NOTE: I may be thinking about this wrong. I may need to pack the VBO one 
    # vertex at a time. 
    self._data.extend(
      (
        *v.to_tuple(),
        *q.to_tuple()
      )
    )

    self._index.append(self._line_counter.value())
    self._line_counter.increment()

  def print(self) -> None:
    raise NotImplementedError()

  