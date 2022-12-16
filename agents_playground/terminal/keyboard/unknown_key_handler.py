from agents_playground.terminal.keyboard.key_handler import KeyHandler, KeyHandlerException
from agents_playground.terminal.keyboard.types import KeyCode

class UnknownKeyHandler(KeyHandler):
  def __init__(self) -> None:
    super().__init__()

  def match(self, key_code: KeyCode) -> bool:
    """Determine if the handler is a match for the key code."""
    return True

  def handle(self, key_code: KeyCode) -> str | None:
    """Processes the key code and returns the corresponding string value."""
    return None