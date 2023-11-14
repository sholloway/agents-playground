"""
This module provides the orchestration for the top level window for the 
Playground UI.
"""

import wx
import wgpu
import wgpu.backends.rs

from agents_playground.ui.sim_window import SimWindow

class Playground:
  def __init__(self) -> None:
    self._app = wx.App()
    self._window = SimWindow()

  def launch(self) -> None:
    self._app.MainLoop()