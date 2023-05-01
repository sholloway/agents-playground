
from typing import Callable, Dict
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics

from agents_playground.likelihood.coin import Coin

class SimulationExtensions:
  def __init__(self) -> None:
    self._entity_extensions: Dict[str, Callable] = {}
    self._renderer_extensions: Dict[str, Callable] = {}
    self._task_extensions: Dict[str, Callable] = {}
    self._coin_extensions:  Dict[str, Coin] = {}
    self._agent_state_transition_extensions:  Dict[str, Callable[[AgentCharacteristics],bool]] = {}

  def reset(self) -> None:
    self._entity_extensions.clear()
    self._renderer_extensions.clear()
    self._task_extensions.clear()
    self._coin_extensions.clear()
    self._agent_state_transition_extensions.clear()

  def register_entity(self, label: str, entity: Callable) -> None:
    self._entity_extensions[label] = entity
  
  def register_renderer(self, label: str, renderer: Callable) -> None:
    self._renderer_extensions[label] = renderer
  
  def register_task(self, label: str, task: Callable) -> None:
    self._task_extensions[label] = task
  
  def register_coin(self, label: str, coin: Coin) -> None:
    self._coin_extensions[label] = coin
  
  def register_transition_condition(self, label: str, condition: Callable[[AgentCharacteristics],bool]) -> None:
    self._agent_state_transition_extensions[label] = condition

  @property
  def entity_extensions(self) -> Dict[str, Callable]:
    return self._entity_extensions
  
  @property
  def renderer_extensions(self) -> Dict[str, Callable]:
    return self._renderer_extensions
  
  @property
  def task_extensions(self) -> Dict[str, Callable]:
    return self._task_extensions
  
  @property
  def coin_extensions(self) -> Dict[str, Coin]:
    return self._coin_extensions
  
  @property
  def agent_state_transition_extensions(self) -> Dict[str, Callable[[AgentCharacteristics], bool]]:
    return self._agent_state_transition_extensions
  
_simulation_extensions = SimulationExtensions()

def simulation_extensions():
  return _simulation_extensions

def register_renderer(label: str) -> Callable:
  """Registers a function as a renderer that can be associated in a scene.
  
  Args:
    - label: The name to assign to the function. This is what it is referred to as in the scene file.
  """
  def decorator_register_renderer(func: Callable) -> Callable:
    _simulation_extensions.register_renderer(label, func)
    return func
  return decorator_register_renderer

def register_entity(label: str) -> Callable:
  """Registers a function as a entity that can be associated in a scene.
  
  Args:
    - label: The name to assign to the function. This is what it is referred to as in the scene file.
  """
  def decorator_register_entity(func: Callable) -> Callable:
    _simulation_extensions.register_entity(label, func)
    return func
  return decorator_register_entity

def register_task(label: str) -> Callable:
  """Registers a function as a task that can be associated in a scene.
  
  Args:
    - label: The name to assign to the function. This is what it is referred to as in the scene file.
  """
  def decorator_register_task(func: Callable) -> Callable:
    _simulation_extensions.register_task(label, func)
    return func
  return decorator_register_task

def register_state_transition_condition(label: str) -> Callable:
  """Registers a function as a state transition condition.
  
  Args:
    - label: The name to assign to the function. This is what it is referred to as in the scene file.
  """
  def decorator_register_state_transition_condition(func: Callable[[AgentCharacteristics],bool]) -> Callable[[AgentCharacteristics],bool]:
    _simulation_extensions.register_transition_condition(label, func)
    return func
  return decorator_register_state_transition_condition
