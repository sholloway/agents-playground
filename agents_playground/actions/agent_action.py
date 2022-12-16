from abc import ABC, abstractmethod
from typing import Callable

from agents_playground.agents.agent import Agent
from agents_playground.core.callable_utils import CallableUtility

# Actions should modify agents. This will help decouple Agents 
# from knowing too much about the terrain.
# TODO: This probably needs to live in a different file.
class AgentAction(ABC):
  def __init__(self) -> None:
    super().__init__()
    self._before_action: Callable | None = None
    self._after_action:  Callable | None = None

  def run(self, agent: Agent, **data) -> None:
    CallableUtility.invoke(self._before_action, data)
    self._perform(agent, **data)
    CallableUtility.invoke(self._after_action, data)

  @abstractmethod
  def _perform(self, agent: Agent, **data) -> None:
    """An instruction for an agent to do something."""

  @property
  def before_action(self) -> Callable | None:
    return self._before_action

  @before_action.setter
  def before_action(self, action: Callable | None) -> None:
    self._before_action = action
  
  @property
  def after_action(self) -> Callable | None:
    return self._after_action

  @before_action.setter
  def after_action(self, action: Callable | None) -> None:
    self._after_action = action
