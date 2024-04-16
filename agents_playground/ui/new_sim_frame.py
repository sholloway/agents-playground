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

GRID_BOARDER = 5
class NewSimFrame(wx.Frame):
  def __init__(self):
    super().__init__(None, title=NEW_SIM_FRAME_TITLE)
    self._build_ui()
    self.Show()

  def _build_ui(self) -> None:
    self.SetSize(600, 500)
    grid_sizer = wx.GridBagSizer()
    self._panel = wx.Panel(self)

    # Picker for where to save the simulation project.
    sp: wx.StandardPaths = wx.StandardPaths.Get()
    self._dir_picker = wx.DirPickerCtrl(self._panel, path=sp.GetDocumentsDir())

    # Simulation Name Input
    # Rules: Lower Case only, 1-z, _, no spaces
    self._sim_name_label = wx.StaticText(self._panel, label="Simulation Name")
    self._sim_name_input = wx.TextCtrl(
      self._panel, 
      value="my_simulation", 
      validator=PatternValidator(ALLOWED_SIM_NAME_PATTERN)
    )

    # Simulation Title
    self._sim_title_label = wx.StaticText(self._panel, label="Simulation Title")
    self._sim_title_input = wx.TextCtrl(
      self._panel, 
      value="My Simulation"
    )
    
    # Simulation Description
    self._sim_description_label = wx.StaticText(self._panel, label="Simulation Description")
    self._sim_description_input = wx.TextCtrl(
      self._panel, 
      value="", 
      style = wx.TE_MULTILINE
    )

    # Create Button
    self._create_button = wx.Button(self._panel, label="Create")

    grid_sizer.Add(self._dir_picker, pos=(1,1), span=(1,2), flag = wx.EXPAND | wx.ALL, border=GRID_BOARDER)
    grid_sizer.Add(self._sim_name_label, pos=(2,1), span=(1,1), flag = wx.ALL, border=GRID_BOARDER)
    grid_sizer.Add(self._sim_name_input, pos=(2,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=GRID_BOARDER)
    
    grid_sizer.Add(self._sim_title_label, pos=(3,1), span=(1,1), flag = wx.ALL, border=GRID_BOARDER)
    grid_sizer.Add(self._sim_title_input, pos=(3,2), span=(1,1), flag = wx.EXPAND | wx.ALL, border=GRID_BOARDER)
    
    grid_sizer.Add(self._sim_description_label, pos=(4,1), span=(1,1), flag = wx.ALL, border=GRID_BOARDER)
    grid_sizer.Add(self._sim_description_input, pos=(5,1), span=(1,2), flag = wx.EXPAND | wx.ALL, border=GRID_BOARDER)
    
    grid_sizer.Add(self._create_button, pos=(6,2), span=(1,2), flag = wx.ALIGN_RIGHT | wx.ALL, border=GRID_BOARDER)

    grid_sizer.AddGrowableCol(2)
    grid_sizer.AddGrowableRow(5)

    self._panel.SetSizerAndFit(grid_sizer)

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