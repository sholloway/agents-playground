from abc import abstractmethod
from typing import Protocol

class Mesh(Protocol):
  @property
  @abstractmethod
  def vertices(self) -> list[float]:
    ...
  
  @property
  @abstractmethod
  def index(self) -> list[int]:
    ...