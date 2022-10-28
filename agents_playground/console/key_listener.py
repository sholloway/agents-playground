"""
Module responsible for listening to key events and converting them to characters.
"""

import dearpygui.dearpygui as dpg

def which_key(uppercase_key_code) -> str:
  """Given a key code return the matching character."""
  """
  Use Cases:
  1. a-z 
  2. Shift + a-z
  3. `, 1-0, -, =, [,],\,;,', , . /
  4. ~, !, @, #, $, %, ^, &, *, (,), _, +
  5. <delete>
  6. <return>
  7. <esc>
  8. <spacebar>
  9. Caps Lock + a - z
  10. Control + v
  """


  # https://www.reddit.com/r/Python/comments/3cw432/looking_for_a_module_that_converts_key_code_to/
  if dpg.is_key_down(key = dpg.mvKey_Shift) or dpg.is_key_down(key = dpg.mvKey_Capital):
    display_ch = uppercase_key_code
  else:
    # ASCII key codes use a single bit position between upper and lower case so 
    # x | 0x20 will force any key to be lower case.
    display_ch = uppercase_key_code | 0x20
  return chr(display_ch)
