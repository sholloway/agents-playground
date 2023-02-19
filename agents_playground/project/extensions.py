
from typing import Callable, Dict

class SimulationExtensions:
  def __init__(self) -> None:
    self._entity_extensions: Dict[str, Callable] = {}
    self._renderer_extensions: Dict[str, Callable] = {}
    self._task_extensions: Dict[str, Callable] = {}

  def reset(self) -> None:
    self._entity_extensions.clear()
    self._renderer_extensions.clear()
    self._task_extensions.clear()

  def register_entity(self, label: str, entity: Callable) -> None:
    self._entity_extensions[label] = entity
  
  def register_renderer(self, label: str, renderer: Callable) -> None:
    self._renderer_extensions[label] = renderer
  
  def register_task(self, label: str, task: Callable) -> None:
    self._task_extensions[label] = task

_simulation_extensions = SimulationExtensions()

def simulation_extensions():
  return _simulation_extensions

def register_renderer(label: str) -> Callable:
  """Registers a function as a renderer that can be associated in a scene.
  
  Args:
    - label: The name to assign to the function. This is what it is referred to as in the scene file.
  """
  def decorator_register_renderer(func) -> Callable:
    _simulation_extensions.register_renderer(label, func)
    return func
  return decorator_register_renderer

def register_entity(label: str) -> Callable:
  """Registers a function as a entity that can be associated in a scene.
  
  Args:
    - label: The name to assign to the function. This is what it is referred to as in the scene file.
  """
  def decorator_register_entity(func) -> Callable:
    _simulation_extensions.register_entity(label, func)
    return func
  return decorator_register_entity

def register_task(label: str) -> Callable:
  """Registers a function as a task that can be associated in a scene.
  
  Args:
    - label: The name to assign to the function. This is what it is referred to as in the scene file.
  """
  def decorator_register_task(func) -> Callable:
    _simulation_extensions.register_task(label, func)
    return func
  return decorator_register_task
