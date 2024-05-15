from typing import Any, List
from agents_playground.terminal.callable import Callable
from agents_playground.terminal.ast.statements import Function
from agents_playground.terminal.environment import Environment
from agents_playground.terminal.interpreter import Interpreter
from agents_playground.terminal.interpreter_runtime_error import ReturnSignal
from agents_playground.terminal.token import Token


class CallableFunction(Callable):
    def __init__(self, declaration: Function, closure: Environment) -> None:
        super().__init__()
        self._declaration = declaration
        self._closure = closure

    def call(self, interpreter: Interpreter, args: List[Any]) -> Any:
        local_env: Environment = Environment(self._closure)
        param_token: Token
        param_value: Any
        for param_token, param_value in zip(self._declaration.params, args):
            local_env.define(param_token.lexeme, param_value)

        try:
            interpreter.execute_block(self._declaration.body, local_env)
        except ReturnSignal as rs:
            return rs.return_value
        return None

    def arity(self) -> int:
        return len(self._declaration.params)

    def __str__(self) -> str:
        return f"<function {self._declaration.name.lexeme}>"
