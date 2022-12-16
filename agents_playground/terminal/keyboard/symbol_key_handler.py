import dearpygui.dearpygui as dpg
from agents_playground.terminal.keyboard.key_handler import KeyHandler, KeyHandlerException
from agents_playground.terminal.keyboard.types import KeyCode

class SymbolKeyHandler(KeyHandler):
  def __init__(self) -> None:
    super().__init__()
    self._keys = {
      39, # '
      44, # ,
      45, # -
      46, # .
      47, # /
      59, # ;
      61, # =
      96, # ``
      91, # [
      93, # ]
      92  # \
    }

  def match(self, key_code: KeyCode) -> bool:
    """Determine if the handler is a match for the key code."""
    return key_code in self._keys

  def handle(self, key_code: KeyCode) -> str | None:
    """Processes the key code and returns the corresponding string value."""
    # Use Case: Shift + Symbol Key
    if dpg.is_key_down(key = dpg.mvKey_Shift):
      match key_code:
        case 39: # '
          return '"'
        case 44: # ,
          return '<'
        case 45: # -
          return '_'
        case 46: # .
          return '>'
        case 47: # /
          return '?'
        case 59: # ;
          return ':'
        case 61: # =
          return '+'
        case 96: # ``
          return '~'
        case 91: # [
          return '{'
        case 93: # ]
          return '}'
        case 92: # \
          return '|'
        case _:
          raise KeyHandlerException(f'SymbolKeyHandler could not process key code {key_code}')
    else:
      # Use Case: Symbol Key.
      return chr(key_code)