"""
Experimental module for having loosely defined agents to support project extensions.
"""

from typing import List, Protocol, Self
from abc import abstractmethod

class AgentAspect(Protocol):
  ...

class AgentLike(Protocol):
  # Perhaps slots would be better?
  # https://wiki.python.org/moin/UsingSlots
  aspects: dict[str, AgentAspect] 

  visible: bool
  
  def transition_state(self) -> None:
    ...

  def reset(self) -> None:
    ...

  def set_visibility(self, is_visible: bool) -> None:
    self.visible = is_visible
    self.handle_state_changed()

  def add_aspect(self, label: str, aspect: AgentAspect) -> Self:
    self.aspects[label] = aspect

  def select(self) -> None:
    self.handle_agent_selected()

  @abstractmethod
  def handle_state_changed(self) -> None:
    ...

  @abstractmethod
  def handle_agent_selected(self) -> None:
    ...