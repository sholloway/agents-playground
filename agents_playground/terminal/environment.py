from __future__ import annotations
from typing import Any, Dict

from agents_playground.terminal.interpreter_runtime_error import InterpreterRuntimeError
from agents_playground.terminal.token import Token

class Environment:
  """A centralized in memory store for variables declared by the Agent Terminal scripts.
  
  The environment provides lexical scoping of variables. The immediate scope is 
  checked first. If a miss occurs, then the wider scope is check and so on until
  the global scope is checked.
  """
  def __init__(self, enclosing: Environment | None = None) -> None:
    self._enclosing: Environment | None = enclosing
    self._in_memory_values: Dict[str, Any] = {
      'None': None
    }

  def define(self, name: str, value: Any) -> None:
    """Declares a variable in the environment."""
    self._in_memory_values[name] = value

  def get(self, name: Token) -> Any:
    """Lookups up the value of a variable."""
    if name.lexeme in self._in_memory_values:
      return self._in_memory_values[name.lexeme]
    elif self._enclosing is not None:
      return self._enclosing.get(name)  
    else:
      raise InterpreterRuntimeError(name, f'Undefined variable \'{name.lexeme}\'.')
    
  def assign(self, name: Token, value: Any) -> None:
    """Assigns a value to an existing variable."""
    if name.lexeme in self._in_memory_values:
      self._in_memory_values[name.lexeme] = value
    elif self._enclosing is not None: 
      self._enclosing.assign(name, value)
    else:
      raise InterpreterRuntimeError(name, f"Undefined variable '{name.lexeme}'.")