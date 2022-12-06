"""
Module responsible for listening to key events and converting them to characters.
"""

import dearpygui.dearpygui as dpg


SYMBOL_CODES = set([
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
    92 # \
  ])

KeyCode = int

class KeyInterpreter:
  """Responsible for converting OS key codes to displayable text."""
  
  def key_to_char(self, key_code: KeyCode) -> str | None:
    """Given a key code return the matching character."""
    # Is it the space bar?
    if key_code == 32:
      return ' '
    
    # Is it the up or down arrow?
    match key_code:
      case 262: # Right Arrow
        return 'RIGHT_ARROW'
      case 263: # Left Arrow
        return 'LEFT_ARROW'
      case 264: # Down Arrow 
        return 'DOWN_ARROW'
      case 265: # Up Arrow 
        return 'UP_ARROW'

    # Is it a control code?
    match key_code:
      case 256: # ESC
        return 'ESC'
      case 258: # Tab
        return '\t'
      case 259: # Back/Delete/Clear
        return '\b'
      case 257 if dpg.is_key_down(key = dpg.mvKey_Shift): # Enter/Return + Shift
        return 'RUN_CODE'
      case 257: # Enter/Return
        return 'NEW_LINE'

    # Is the key in the English Alphabet? 
    # [A-Z]
    alpha_key = (65 <= key_code and key_code <= 90)

    # Use Case Shift + [A-Z] -> [A-Z]
    if alpha_key and dpg.is_key_down(key = dpg.mvKey_Shift):
      return chr(key_code)

    # Caps Lock On + [A-Z] -> [A-Z]
    if alpha_key and dpg.is_key_down(key = dpg.mvKey_Capital):
      return chr(key_code)

    # Alphabet key but not capitalize. 
    # [A-Z] -> [a-z]
    if alpha_key \
      and not dpg.is_key_down(key = dpg.mvKey_Shift) \
      and not dpg.is_key_down(key = dpg.mvKey_Capital):
      """
      ASCII key codes use a single bit position between upper and lower case so 
      x | 0x20 will force any key to be lower case.
      
      For example:
        A is 65 or 1000001
        32 -> 0x20 -> 100000
        1000001 | 100000 -> 1100001 -> 97 -> 'a'
      """
      return chr(key_code | 0x20)

    # Is the key [0 - 9]?
    numeric_key = (48 <= key_code and key_code <= 57)
    if numeric_key \
      and not dpg.is_key_down(key = dpg.mvKey_Shift):
      return chr(key_code)

    # Is the key Shift + [0-9] -> [!, @, #, $, %, ^, &, *, (,) ]
    if numeric_key \
      and dpg.is_key_down(key = dpg.mvKey_Shift):
      match key_code:
        case 0x30:
          return ')'
        case 0x31:
          return '!'
        case 0x32:
          return '@'
        case 0x33:
          return '#'
        case 0x34:
          return '$'
        case 0x35:
          return '%'
        case 0x36:
          return '^'
        case 0x37:
          return '&'
        case 0x38:
          return '*'
        case 0x39:
          return '('
    
    # Is the key a symbol?
    if key_code in SYMBOL_CODES \
      and not dpg.is_key_down(key = dpg.mvKey_Shift):
      return chr(key_code)
    
    if key_code in SYMBOL_CODES \
      and dpg.is_key_down(key = dpg.mvKey_Shift):
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