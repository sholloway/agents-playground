import os
import wx

from agents_playground.ui.components.input_error_popup import InputErrorPopup

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