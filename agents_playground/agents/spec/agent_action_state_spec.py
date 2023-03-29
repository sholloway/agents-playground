from typing import Protocol

class AgentActionStateLike(Protocol):
  name: str

  def __repr__(self) -> str:
    return f'{self.__class__} {self.name}'