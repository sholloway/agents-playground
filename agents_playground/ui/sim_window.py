"""
This module is the top level window for the Playground UI.
It leverages wxPython for the UI framework.
"""

import wx
from agents_playground.ui.wx_patch import WgpuWidget

class SimWindow(wx.Frame):
  def __init__(self) -> None:
    super().__init__(None, title="The Agent's Playground")
    self.SetSize(800, 950)
    self.Show()