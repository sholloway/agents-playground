from typing import Any, Dict

from agents_playground.terminal.interpreter_runtime_error import InterpreterRuntimeError
from agents_playground.terminal.token import Token

class Environment:
  """A centralized in memory store for variables declared by the Agent Terminal scripts."""
  def __init__(self) -> None:
    self._in_memory_values: Dict[str, Any] = dict()

  def define(self, name: str, value: Any) -> None:
    self._in_memory_values[name] = value

  def get(self, name: Token) -> Any:
    if name.lexeme in self._in_memory_values:
      return self._in_memory_values[name.lexeme]
    else:
      raise InterpreterRuntimeError(name, f'Undefined variable \'{name.lexeme}\'.')
    
  def assign(self, name: Token, value: Any) -> None:
    if name.lexeme in self._in_memory_values:
      self._in_memory_values[name.lexeme] = value
    else:
      raise InterpreterRuntimeError(name, f"Undefined variable '{name.lexeme}'.")