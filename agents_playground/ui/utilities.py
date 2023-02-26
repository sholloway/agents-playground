
from typing import Tuple
import dearpygui.dearpygui as dpg

def find_centered_window_position(
  parent_width: int, 
  parent_height: int, 
  child_width: int, 
  child_height: int
) -> Tuple[int]:
  return (
    parent_width/2 - child_width/2,
    parent_height/2 - child_height/2
  )

ERROR_WINDOW_WIDTH: int  = 400
ERROR_WINDOW_HEIGHT: int = 50
SUCCESS_WINDOW_WIDTH: int  = 400
SUCCESS_WINDOW_HEIGHT: int = 50

def create_error_window(error_title: str, error_msg: str) -> None:
  """Creates a modal, centered error window.

  Args:
    - error_title: The title for the window.
    - error_msg: The error message to display.
  """
  position = find_centered_window_position(
    dpg.get_viewport_width(), 
    dpg.get_viewport_height(), 
    ERROR_WINDOW_WIDTH, 
    ERROR_WINDOW_HEIGHT
  )
  dpg.split_frame() # This is for DearPyGUI Issue 1791: https://github.com/hoffstadt/DearPyGui/issues/1791  
  with dpg.window(
    label  = error_title,
    modal  = True, 
    width  = ERROR_WINDOW_WIDTH,
    height = ERROR_WINDOW_HEIGHT,
    show   = True,
    pos    = position
  ):
    dpg.add_text(error_msg, wrap=390)

def create_success_window(title: str, msg: str) -> None:
  """Creates a modal, centered success window.

  Args:
    - title: The title for the window.
    - msg: The  message to display.
  """
  position = find_centered_window_position(
    dpg.get_viewport_width(), 
    dpg.get_viewport_height(), 
    SUCCESS_WINDOW_WIDTH, 
    SUCCESS_WINDOW_HEIGHT
  )
  dpg.split_frame() # This is for DearPyGUI Issue 1791: https://github.com/hoffstadt/DearPyGui/issues/1791  
  with dpg.window(
    label  = title,
    modal  = True, 
    width  = SUCCESS_WINDOW_WIDTH,
    height = SUCCESS_WINDOW_HEIGHT,
    show   = True,
    pos    = position
  ):
    dpg.add_text(msg, wrap=390)