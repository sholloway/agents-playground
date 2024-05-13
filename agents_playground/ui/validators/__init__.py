def keycode_to_value(keycode: int, shift_pressed: bool, caps_lock_on: bool) -> str:
  """Given a keycode returns the related character.

  Note: ASCII key codes use a single bit position between upper and lower case so 
  x | 0x20 will force any key to be lower case.
  
  For example:
    A is 65 or 1000001
    32 -> 0x20 -> 100000
    1000001 | 100000 -> 1100001 -> 97 -> 'a'
  """
  code = keycode if shift_pressed or caps_lock_on else keycode | 0x20
  return chr(code)

from . import *