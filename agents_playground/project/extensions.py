
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
    self._agent_system_extensions: Dict[str, Callable] = {}
    self._agent_context_menu_extensions: Dict[str, Callable] = {}

  def reset(self) -> None:
    self._entity_extensions.clear()
    self._renderer_extensions.clear()
    self._task_extensions.clear()
    self._coin_extensions.clear()
    self._agent_state_transition_extensions.clear()
    self._agent_system_extensions.clear()
    self._agent_context_menu_extensions.clear()

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

  def register_system(self, label: str, system: Callable) -> None:
    self._agent_system_extensions[label] = system
  
  def register_agent_context_menu_extensions(self, label: str, system: Callable) -> None:
    self._agent_context_menu_extensions[label] = system

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
  
  @property
  def agent_system_extensions(self) -> Dict[str, Callable]:
    return self._agent_system_extensions
  
  @property
  def agent_context_menu_extensions(self) -> Dict[str, Callable]:
    return self._agent_context_menu_extensions
  
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

def register_system(label: str) -> Callable:
  """Registers a function as a system that can be associated in a scene.
  
  Args:
    - label: The name to assign to the system. This is what it is referred to as in the scene file.
  """
  def decorator_register_system(func: Callable) -> Callable:
    _simulation_extensions.register_system(label, func)
    return func
  return decorator_register_system

def register_agent_context_menu(label: str) -> Callable:
  """Registers a function as a selected Agent's context menu action.
  The contract for the func must match the DearPyGUI callback specification.
    def my_context_menu_callback(sender, item_data, user_data)
  
  The user_data parameter will be a Dict[str, Any] with the agent_id and Scene 
  injected.
  
  Args:
    - label: The text to assign to the context menu item. 
      This is displayed in the menu.

  Example:
    @register_agent_context_menu(label = 'Menu Item Text')
    def do_stuff(sender, item_data, user_data) -> None:
      print(f'agent_id: {user_data['agent_id']}')
      print(f'Scene Data: {user_data['scene']}')
  """
  def decorator_register_agent_context_menu(func: Callable) -> Callable:
    _simulation_extensions.register_agent_context_menu_extensions(label, func)
    return func
  return decorator_register_agent_context_menu
