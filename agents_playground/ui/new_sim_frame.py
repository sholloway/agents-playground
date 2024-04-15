import re

import wx

NEW_SIM_FRAME_TITLE = 'Create a New Simulation'
ALLOWED_SIM_NAME_PATTERN = r"^([a-z_])+$"

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
  print(f'keycode_to_value: Shift Down({shift_pressed}), Passed Code: {keycode}, Used Code: {code}')
  return chr(code)
  

class PatternValidator(wx.Validator):
  def __init__(self, pattern: str):
    super().__init__()
    self._pattern = pattern
    self._caps_lock_key_down: bool = False
    self.Bind(wx.EVT_KEY_DOWN, self._handle_key_down)
    self.Bind(wx.EVT_KEY_UP, self._handle_key_up)
    self.Bind(wx.EVT_CHAR, self._handle_on_char)

  def Clone(self):
    return PatternValidator(self._pattern)
  
  def _handle_on_char(self, event: wx.KeyEvent) -> None:
    """Only allow proper characters when typing."""
    key_code: int = event.GetKeyCode()
    key_value: str = keycode_to_value(key_code, event.ShiftDown(), self._caps_lock_key_down)
    print(f'_handle_on_char: Key Value({key_value})')
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
    tc = self.GetWindow()
    value = tc.GetValue()
    print('Validating')
    match = re.match(self._pattern, value)
    return match is not None
  
  def TransferToWindow(self):
    """ 
    Transfer data from validator to window.
    The default implementation returns False, indicating that an error
    occurred.  We simply return True, as we don't do any data transfer.
    """
    return True # Prevent wxDialog from complaining.

  def TransferFromWindow(self):
    """ 
    Transfer data from window to validator.
    The default implementation returns False, indicating that an error
    occurred.  We simply return True, as we don't do any data transfer.
    """
    return True # Prevent wxDialog from complaining.

class NewSimFrame(wx.Frame):
  def __init__(self):
    super().__init__(None, title=NEW_SIM_FRAME_TITLE)
    self._build_ui()
    self.Show()

  def _build_ui(self) -> None:
    # self.SetSize(1600, 900)
    top_level_sizer = wx.BoxSizer(wx.VERTICAL)
    self._panel = wx.Panel(self)
    self._panel.SetSizer(top_level_sizer)

    # Simulation Name Input
    # Rules: Lower Case only, 1-z, _, no spaces
    sim_name_label = wx.StaticText(self._panel, label="Simulation Name")
    sim_name_input = wx.TextCtrl(
      self._panel, 
      value="my_simulation", 
      size=(125, -1), 
      validator=PatternValidator(ALLOWED_SIM_NAME_PATTERN)
    )
    top_level_sizer.Add(sim_name_label, proportion=1, flag = wx.EXPAND)
    top_level_sizer.Add(sim_name_input, proportion=1, flag = wx.EXPAND)

    # Picker for where to save the simulation project.
    sp: wx.StandardPaths = wx.StandardPaths.Get()
    self._dir_picker = wx.DirPickerCtrl(self._panel, path=sp.GetDocumentsDir())
    top_level_sizer.Add(self._dir_picker, proportion = 1, flag = wx.EXPAND) 

  def _select_directory(self) -> None:
    sp: wx.StandardPaths = wx.StandardPaths.Get()
    
    sim_picker = wx.DirDialog(
      parent=self,
      message = "Create a New Simulation",
      defaultPath=sp.GetDocumentsDir(),
      style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR
    )

    if sim_picker.ShowModal() == wx.ID_OK:
      sim_path = sim_picker.GetPath()
      # Do something here...

    sim_picker.Destroy()