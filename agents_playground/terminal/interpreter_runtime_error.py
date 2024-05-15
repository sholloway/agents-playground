from typing import Any
from agents_playground.terminal.token import Token


class InterpreterRuntimeError(Exception):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(*args)
        self._token = token

    @property
    def token(self) -> Token:
        return self._token


class ControlFlowSignal(Exception):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(*args)
        self._token = token

    @property
    def token(self) -> Token:
        return self._token


class BreakStatementSignal(ControlFlowSignal):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(token, *args)


class ContinueStatementSignal(ControlFlowSignal):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(token, *args)


class ReturnSignal(ControlFlowSignal):
    def __init__(self, token: Token, return_value: Any, *args: object) -> None:
        super().__init__(token, *args)
        self._return_value = return_value

    @property
    def return_value(self) -> Any:
        return self._return_value
