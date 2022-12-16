from agents_playground.terminal.keyboard.key_handler import KeyHandler, KeyHandlerException
from agents_playground.terminal.keyboard.types import KeyCode

class ArrowKeyHandler(KeyHandler):
  def __init__(self) -> None:
    super().__init__()
    self._keys = {262, 263, 264, 265}
    
  def match(self, key_code: KeyCode) -> bool:
    """Determine if the handler is a match for the key code."""
    return key_code in self._keys

  def handle(self, key_code: KeyCode) -> str | None:
    """Processes the key code and returns the corresponding string value."""
    match key_code:
      case 262: # Right Arrow
        return 'RIGHT_ARROW'
      case 263: # Left Arrow
        return 'LEFT_ARROW'
      case 264: # Down Arrow 
        return 'DOWN_ARROW'
      case 265: # Up Arrow 
        return 'UP_ARROW'
      case _:
        raise KeyHandlerException(f'ArrowKeyHandler could not process key code {key_code}')
