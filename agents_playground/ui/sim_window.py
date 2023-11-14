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

    # Add Menu Bar.
    menu_bar = wx.MenuBar()
    # Menu: Simulations -> New | Open
    sim_menu = wx.Menu()
    sim_menu.Append(id=101, item="New", helpString="Create a new simulation project.")
    sim_menu.Append(id=102, item="Open", helpString="Open an existing simulation project.")
    menu_bar.Append(sim_menu, "Simulations")
    self.SetMenuBar(menu_bar)
    self.CreateStatusBar()
    # After it Launches: Layers Menu, Buttons: Start/Stop, Toggle Fullscreen, Utility
    
    # Add Canvas
    # Add Context Menu 
    # Add status bar