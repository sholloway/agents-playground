
from types import MethodType, SimpleNamespace
from typing import Any, List, Tuple
import dearpygui.dearpygui as dpg

from agents_playground.renderers.color import BasicColors, Color

def find_centered_window_position(
  parent_width: int, 
  parent_height: int, 
  child_width: int, 
  child_height: int
) -> Tuple[int, int]:
  center = (
    int(parent_width/2 - child_width/2),
    int(parent_height/2 - child_height/2)
  )
  return center

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

def add_tree_table(label:str, data: Any) -> None:
  with dpg.tree_node(label = label):
    with dpg.table(
      header_row=True, 
      policy=dpg.mvTable_SizingFixedFit,
      row_background=True, 
      borders_innerH=True, 
      borders_outerH=True, 
      borders_innerV=True,
      borders_outerV=True
    ):
      dpg.add_table_column(label="Field", width_fixed=True)
      dpg.add_table_column(label="Value", width_stretch=True, init_width_or_weight=0.0)
      items_dict = data if isinstance(data, dict) else data.__dict__
      for k, v in items_dict.items():
        with dpg.table_row():
          dpg.add_text(k)
          match v:
            case Color():
              dpg.add_color_button(v)
            case bool():
              if v:
                dpg.add_text(str(v), color=BasicColors.green.value)
              else:
                dpg.add_text(str(v), color=BasicColors.red.value)
            case _ :
              dpg.add_text(v, wrap = 500)

def add_table_of_namespaces(
  label:str, 
  columns: List[str], 
  rows: List[SimpleNamespace]
) -> None:
  with dpg.tree_node(label = label):
    with dpg.table(
      header_row=True, 
      policy=dpg.mvTable_SizingFixedFit,
      row_background=True, 
      borders_innerH=True, 
      borders_outerH=True, 
      borders_innerV=True,
      borders_outerV=True
    ):
      for col in columns:
        dpg.add_table_column(label=col, width_fixed=True)

      for row in rows: 
        with dpg.table_row():
          for v in row.__dict__.values():
            match v:
              case Color():
                dpg.add_color_button(v)
              case bool():
                if v:
                  dpg.add_text(str(v), color=BasicColors.green.value)
                else:
                  dpg.add_text(str(v), color=BasicColors.red.value)
              case MethodType():
                dpg.add_text('bound method')
              case _ :
                dpg.add_text(v, wrap=500)