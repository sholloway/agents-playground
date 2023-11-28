"""
This module provides the orchestration for the top level window for the 
Playground UI.
"""

import wx

from agents_playground.ui.sim_frame import SimFrame

class Playground(wx.App):
  def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
    super().__init__(redirect, filename, useBestVisual, clearSigInt)
    # This catches events when the app is asked to activate by some other process.
    self.Bind(wx.EVT_ACTIVATE_APP, self._on_activate)
    

  def _on_activate(self, event):
    # Handle the activate event, rather than something else, like iconize.
    if event.GetActive():
      self._bring_window_to_front()
    event.Skip()

  def _bring_window_to_front(self):
    try: 
      # Note: It's possible for this event to come when the frame is closed.
      self.GetTopWindow().Raise()
    except:
        pass
    
  def OnInit(self) -> bool:
    """wx.App lifecycle method."""
    self.sim_frame = SimFrame()
    self.sim_frame.Show()
    return True
  
  def MacOpenFile(self, filename: str) -> None:
    """wx.App method. Called for files dropped on dock icon, or opened via finders context menu"""
    pass

  def MacReopenApp(self) -> None:
    """wx.App method. Called when the doc icon is clicked, and ???"""
    self._bring_window_to_front()

  def MacNewFile(self) -> None:
    pass
    
  def MacPrintFile(self, file_path:str) -> None:
    pass