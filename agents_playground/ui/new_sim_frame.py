from __future__ import annotations
import os 
from pathlib import Path 
import re

import wx

ALLOWED_SIM_NAME_PATTERN    = r"^([a-z_])+$"
NEW_SIM_GRID_BOARDER        = 5
NEW_SIM_FRAME_TITLE         = 'Create a New Simulation'
NEW_SIM_DIR_TOOLTIP         = 'Specify where the new simulation should be created.'
NEW_SIM_NAME_TOOLTIP        = 'Assign a unique name for the simulation. This is the name of the simulation file.'
NEW_SIM_TITLE_TOOLTIP       = 'Assign a unique title for the simulation. This will be displayed in the Simulation menu.'
NEW_SIM_DESCRIPTION_TOOLTIP = 'Describe what the simulation does. This will be displayed in the Simulation window.'
NEW_SIM_NAME_FORMAT_ERROR   = "Only the lower case characters a-1 and the _ character are allowed."
NEW_SIM_TITLE_FORMAT_ERROR  = "The title cannot be empty."
NEW_SIM_DESCRIPTION_FORMAT_ERROR  = "The description cannot be empty."
NEW_SIM_DIR_FORMAT_ERROR  = "The directory must exist."

def keycode_to_value(keycode: int, shift_pressed: bool, caps_lock_on: bool) -> str:
  """Given a keycode returns the character"""

  """
  Note: ASCII key codes use a single bit position between upper and lower case so 
  x | 0x20 will force any key to be lower case.
  
  For example:
    A is 65 or 1000001
    32 -> 0x20 -> 100000
    1000001 | 100000 -> 1100001 -> 97 -> 'a'
  """
  code = keycode if shift_pressed or caps_lock_on else keycode | 0x20
  return chr(code)

class InputErrorPopup(wx.PopupTransientWindow):
  def __init__(self, parent: wx.Window, style: int, error_msg: str, font: wx.Font):
    super().__init__(parent, style)
    self._panel = wx.Panel(self)
    self._panel.SetBackgroundColour('#FFB6C1')

    error_label = wx.StaticText(self._panel, label='Input Error')
    error_msg_component = wx.StaticText(self._panel, label=error_msg)
    
    error_label.SetFont(font.Bold())
    error_label.SetForegroundColour('black')
    error_msg_component.SetFont(font)
    error_msg_component.SetForegroundColour('black')
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(error_label, flag = wx.ALL, border = 5)
    sizer.Add(error_msg_component, flag = wx.ALL, border = 5)
    
    self._panel.SetSizer(sizer)
    sizer.Fit(self._panel)
    sizer.Fit(self)
    self.Layout()
    
class CannotBeEmptyValidator(wx.Validator):
  def __init__(
    self, 
    error_msg: str, 
    background_color: tuple[int,...], 
    foreground_color: tuple[int,...]
  ) -> None:
    super().__init__()
    self._error_msg = error_msg
    self._original_background_color = background_color
    self._original_text_color = foreground_color

  def Clone(self):
    return CannotBeEmptyValidator(
      self._error_msg, 
      self._original_background_color, 
      self._original_text_color)
  
  def Validate(self, win):
    """Called when the parent component does a self.Validate()"""
    component = self.GetWindow()
    value: str = component.GetValue()
    valid = len(value.strip()) > 0
    if valid:
      component.SetBackgroundColour(self._original_background_color) 
      component.SetForegroundColour(self._original_text_color) 
      component.Refresh()
    else:
      error_popup = InputErrorPopup(
        parent    = component, 
        style     = wx.NO_BORDER, 
        error_msg = self._error_msg,
        font      = component.GetFont()
      )

      component_pos = component.ClientToScreen( (0,0) )
      component_size =  component.GetSize()
      error_popup.Position(component_pos, (0, component_size[1]))
      error_popup.Popup()

      component.SetForegroundColour('black')
      component.SetBackgroundColour('pink')
      component.SetFocus()
      component.Refresh()
    return valid
  
  def TransferToWindow(self):
    return True

  def TransferFromWindow(self):
    return True 

class DirectoryMustExistValidator(wx.Validator):
  def __init__(
    self, 
    error_msg: str, 
    background_color: tuple[int,...], 
    foreground_color: tuple[int,...]
  ) -> None:
    super().__init__()
    self._error_msg = error_msg
    self._original_background_color = background_color
    self._original_text_color = foreground_color

  def Clone(self):
    return DirectoryMustExistValidator(
      self._error_msg, 
      self._original_background_color, 
      self._original_text_color)
  
  def Validate(self, win):
    """Called when the parent component does a self.Validate()"""
    component = self.GetWindow()
    selected_path: str = component.GetPath()
    print(selected_path)
    valid = os.path.isdir(selected_path)
    if valid:
      component.SetBackgroundColour(self._original_background_color) 
      component.SetForegroundColour(self._original_text_color) 
      component.Refresh()
    else:
      error_popup = InputErrorPopup(
        parent    = component, 
        style     = wx.NO_BORDER, 
        error_msg = self._error_msg,
        font      = component.GetFont()
      )

      component_pos = component.ClientToScreen( (0,0) )
      component_size =  component.GetSize()
      error_popup.Position(component_pos, (0, component_size[1]))
      error_popup.Popup()

      component.SetForegroundColour('black')
      component.SetBackgroundColour('pink')
      component.SetFocus()
      component.Refresh()
    return valid
  
  def TransferToWindow(self):
    return True

  def TransferFromWindow(self):
    return True 

class PatternValidator(wx.Validator):
  def __init__(
    self, 
    pattern: str, 
    error_msg: str, 
    background_color: tuple[int,...], 
    foreground_color: tuple[int,...]
  ) -> None:
    super().__init__()
    self._pattern = pattern
    self._error_msg = error_msg
    self._caps_lock_key_down: bool = False
    self._original_background_color = background_color
    self._original_text_color = foreground_color
    self.Bind(wx.EVT_KEY_DOWN, self._handle_key_down)
    self.Bind(wx.EVT_KEY_UP, self._handle_key_up)
    self.Bind(wx.EVT_CHAR, self._handle_on_char)

  def Clone(self):
    return PatternValidator(
      self._pattern, 
      self._error_msg, 
      self._original_background_color, 
      self._original_text_color
    )

  def _handle_on_char(self, event: wx.KeyEvent) -> None:
    """Only allow proper characters when typing."""
    key_code: int = event.GetKeyCode()
    key_value: str = keycode_to_value(key_code, event.ShiftDown(), self._caps_lock_key_down)
    if key_code == wx.WXK_DELETE or re.match(self._pattern, key_value) is not None:
      event.Skip()
    return
  
  def _handle_key_down(self, event: wx.KeyEvent) -> None:
    keycode = event.GetKeyCode()
    if keycode == wx.WXK_CAPITAL:
      self._caps_lock_key_down = True
    event.Skip()
    return 
  
  def _handle_key_up(self, event: wx.KeyEvent) -> None:
    keycode = event.GetKeyCode()
    if keycode == wx.WXK_CAPITAL:
      self._caps_lock_key_down = False
    event.Skip()
    return 

  def Validate(self, win):
    """Called when the parent component does a self.Validate()"""
    component = self.GetWindow()
    value = component.GetValue()
    match = re.match(self._pattern, value)
    if match:
      component.SetBackgroundColour(self._original_background_color) 
      component.SetForegroundColour(self._original_text_color) 
      component.Refresh()
    else:
      error_popup = InputErrorPopup(
        parent    = component, 
        style     = wx.NO_BORDER, 
        error_msg = self._error_msg,
        font      = component.GetFont()
      )

      component_pos = component.ClientToScreen( (0,0) )
      component_size =  component.GetSize()
      error_popup.Position(component_pos, (0, component_size[1]))
      error_popup.Popup()

      component.SetForegroundColour('black')
      component.SetBackgroundColour('pink')
      component.SetFocus()
      component.Refresh()
    return match is not None
  
  def TransferToWindow(self):
    return True 

  def TransferFromWindow(self):
    return True 


class NewSimFrame(wx.Frame):
  def __init__(self, parent):
    super().__init__(parent = parent, title=NEW_SIM_FRAME_TITLE, style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT )
    self._build_ui()
    self.CenterOnParent()
    self.Show()

  def _build_ui(self) -> None:
    self.SetSize(600, 500)
    grid_sizer = wx.GridBagSizer()
    self._panel = wx.Panel(self)

    # Simulation Description
    # Creating this first to use its colors on the other components.
    self._sim_description_label = wx.StaticText(self._panel, label="Simulation Description")
    self._sim_description_input = wx.TextCtrl(
      self._panel, 
      value="", 
      style = wx.TE_MULTILINE,
    )
    self._sim_description_input.SetToolTip(NEW_SIM_DESCRIPTION_TOOLTIP)
    self._sim_description_input.SetValidator(
      CannotBeEmptyValidator(
        NEW_SIM_DESCRIPTION_FORMAT_ERROR, 
        self._sim_description_input.GetBackgroundColour(),
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
      )
    )
    
    # Picker for where to save the simulation project.
    sp: wx.StandardPaths = wx.StandardPaths.Get()
    self._dir_picker = wx.DirPickerCtrl(self._panel, path=sp.GetDocumentsDir())
    self._dir_picker.SetToolTip(NEW_SIM_DIR_TOOLTIP)
    self._dir_picker.SetValidator(
      DirectoryMustExistValidator(
        NEW_SIM_DIR_FORMAT_ERROR,
        self._sim_description_input.GetBackgroundColour(),
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
      )
    )

    # Simulation Name Input
    # Input Rules: Lower Case only, a-z, _, no spaces
    self._sim_name_label = wx.StaticText(self._panel, label="Simulation Name")
    self._sim_name_input = wx.TextCtrl(
      self._panel, 
      value="my_simulation", 
      validator=PatternValidator(
        ALLOWED_SIM_NAME_PATTERN, 
        NEW_SIM_NAME_FORMAT_ERROR, 
        self._sim_description_input.GetBackgroundColour(),
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
      )
    )
    self._sim_name_input.SetToolTip(NEW_SIM_NAME_TOOLTIP)  

    # Simulation Title
    self._sim_title_label = wx.StaticText(self._panel, label="Simulation Title")
    self._sim_title_input = wx.TextCtrl(
      self._panel, 
      value="My Simulation",
      validator = CannotBeEmptyValidator(
        NEW_SIM_TITLE_FORMAT_ERROR, 
        self._sim_description_input.GetBackgroundColour(),
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
      )
    )
    self._sim_title_input.SetToolTip(NEW_SIM_TITLE_TOOLTIP)
    
    
    # Set all the input boxes to have the same color. There is a weird quirk with 
    # wxPython that it creates a multiline TextCtrl with a different color than 
    # a single line. 
    self._sim_title_input.SetBackgroundColour(self._sim_description_input.GetBackgroundColour())
    self._sim_name_input.SetBackgroundColour(self._sim_description_input.GetBackgroundColour())

    # Create Button
    self._create_button = wx.Button(self._panel, label="Create")
    self._create_button.Bind(wx.EVT_BUTTON, self._handle_clicked_create_button)

    grid_sizer.Add(self._dir_picker, pos=(1,1), span=(1,2), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._sim_name_label, pos=(2,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._sim_name_input, pos=(2,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._sim_title_label, pos=(3,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._sim_title_input, pos=(3,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._sim_description_label, pos=(4,1), span=(1,1), flag = wx.ALL, border=NEW_SIM_GRID_BOARDER)
    grid_sizer.Add(self._sim_description_input, pos=(5,1), span=(1,2), flag = wx.EXPAND | wx.ALL, border=NEW_SIM_GRID_BOARDER)
    
    grid_sizer.Add(self._create_button, pos=(6,2), span=(1,2), flag = wx.ALIGN_RIGHT | wx.ALL, border=NEW_SIM_GRID_BOARDER)

    grid_sizer.AddGrowableCol(2)
    grid_sizer.AddGrowableRow(5)

    self._panel.SetSizerAndFit(grid_sizer)

  def _handle_clicked_create_button(self, event) -> None:
    """
    Event handler for clicking the Create Simulation button.

    Validates that the selected directory exits, the name is valid, and the title isn't empty.
    If all inputs are valid, then it attempts to create a new simulation. 
    """
    if self.Validate():
      try:
        NewSimulationBuilder().build()
      except NewSimulationBuilderException as e:
        wx.MessageBox(
          message = f'There was an error while trying to create a new simulation.\nThe error was.\n{str(e)}',
          caption = 'Error',
          parent  = self,
          style   = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE
        )

class NewSimulationBuilderException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class NewSimulationBuilder:
  def build(self) -> None:
    raise NewSimulationBuilderException('Hi Mom')