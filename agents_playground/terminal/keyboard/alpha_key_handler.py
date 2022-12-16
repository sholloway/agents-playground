import dearpygui.dearpygui as dpg
from agents_playground.terminal.keyboard.key_handler import KeyHandler, KeyHandlerException
from agents_playground.terminal.keyboard.types import KeyCode

class AlphaKeyHandler(KeyHandler):
  def __init__(self) -> None:
    super().__init__()

  def match(self, key_code: KeyCode) -> bool:
    """Determine if the handler is a match for the key code."""
    return 65 <= key_code and key_code <= 90

  def handle(self, key_code: KeyCode) -> str | None:
    """Processes the key code and returns the corresponding string value."""
    shift_down = dpg.is_key_down(key = dpg.mvKey_Shift)
    caps_lock_on = dpg.is_key_down(key = dpg.mvKey_Capital)
    # Use Case: Shift + [A-Z] -> [A-Z]
    if shift_down:
      return chr(key_code)
    elif caps_lock_on:
      # Use Case: Caps Lock On + [A-Z] -> [A-Z]
      return chr(key_code)
    elif not shift_down and not caps_lock_on:
      # Alphabet key but not capitalize. 
      # Use Case: [A-Z] -> [a-z]
      """
      ASCII key codes use a single bit position between upper and lower case so 
      x | 0x20 will force any key to be lower case.
      
      For example:
        A is 65 or 1000001
        32 -> 0x20 -> 100000
        1000001 | 100000 -> 1100001 -> 97 -> 'a'
      """
      return chr(key_code | 0x20)
    else:
      raise KeyHandlerException(f'AlphaKeyHandler could not process key code {key_code}')
