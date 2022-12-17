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