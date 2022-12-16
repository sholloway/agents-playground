from agents_playground.terminal.keyboard.key_handler import KeyHandler
from agents_playground.terminal.keyboard.types import KeyCode

class SpaceKeyHandler(KeyHandler):
  def __init__(self) -> None:
    super().__init__()

  def match(self, key_code: KeyCode) -> bool:
    """Determine if the handler is a match for the key code."""
    return key_code == 32

  def handle(self, key_code: KeyCode) -> str | None:
    """Processes the key code and returns the corresponding string value."""
    return ' '