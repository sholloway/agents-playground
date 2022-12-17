
from typing import Any, List
from agents_playground.terminal.Callable import Callable
from agents_playground.terminal.ast.statements import Function
from agents_playground.terminal.environment import Environment
from agents_playground.terminal.interpreter import Interpreter
from agents_playground.terminal.token import Token

class CallableFunction(Callable):
  def __init__(self, declaration: Function) -> None:
    super().__init__()
    self._declaration = declaration

  def call(self, interpreter: Interpreter, args: List[Any]) -> Any:
    local_env: Environment = Environment(interpreter.globals)
    param_token: Token
    param_value: Any
    for param_token, param_value in zip(self._declaration.params, args):
      local_env.define(param_token.lexeme, param_value)
    interpreter.execute_block(self._declaration.body, local_env)
    return None;

  def arity(self) -> int:
    return len(self._declaration.params)

  def __str__(self) -> str:
    return f"<function {self._declaration.name.lexeme}>"