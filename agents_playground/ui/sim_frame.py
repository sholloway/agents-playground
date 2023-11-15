"""
This module is the top level window for the Playground UI.
It leverages wxPython for the UI framework.
"""

from enum import IntEnum

import wx
from agents_playground.ui.wx_patch import WgpuWidget


class SimMenuItems(IntEnum):
  NEW_SIM = 1000
  OPEN_SIM = 1001

class SimFrame(wx.Frame):
  def __init__(self) -> None:
    super().__init__(None, title="The Agent's Playground")
    self.SetSize(800, 950)
    self.Show()

    # Add Menu Bar.
    self.menu_bar = wx.MenuBar()
    
    # Build the File Menu
    # Menu: File -> New | Open
    self.file_menu = wx.Menu()
    self.file_menu.Append(id=SimMenuItems.NEW_SIM, item="New Simulation...", helpString="Create a new simulation project.")
    self.file_menu.Append(id=SimMenuItems.OPEN_SIM, item="Open Simulation...", helpString="Open an existing simulation project.")
    self.file_menu.Append(id=wx.ID_PREFERENCES, item="&Preferences", helpString="Set the Playground preferences.") # Note: On the Mac this displays on the App Menu.
    
    # Build the Help Menu
    self.help_menu = wx.Menu()
    self.help_menu.Append(id=wx.ID_ABOUT, item="&About MyApp") # Note: On the Mac this displays on the App Menu.

    self.menu_bar.Append(self.file_menu, "&File")
    self.menu_bar.Append(self.help_menu, "&Help")

    self.SetMenuBar(self.menu_bar)

    self.Bind(wx.EVT_MENU, self._handle_new_sim, id=SimMenuItems.NEW_SIM)
    self.Bind(wx.EVT_MENU, self._handle_open_sim, id=SimMenuItems.OPEN_SIM)
    self.Bind(wx.EVT_MENU, self._handle_about_request, id=wx.ID_ABOUT) 
    self.Bind(wx.EVT_MENU, self._handle_preferences, id=wx.ID_PREFERENCES) 
    # After it Launches: Layers Menu, Buttons: Start/Stop, Toggle Fullscreen, Utility
    
    # Add Canvas
    # Add Context Menu 
    # Add status bar
    self.CreateStatusBar()

  def _handle_new_sim(self, event) -> None:
    print(f'Clicked New: {type(event)}, {event}')

  def _handle_open_sim(self, event) -> None:
    print(f'Clicked Open: {type(event)}, {event}')
    sp: wx.StandardPaths = wx.StandardPaths.Get()
    
    dialog = wx.DirDialog(
      parent=self,
      message = "Open a Simulation",
      defaultPath=sp.GetDocumentsDir(),
      style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR
    )

    if dialog.ShowModal() == wx.ID_OK:
      print(dialog.GetPath())
    
    dialog.Destroy()

  def _handle_about_request(self, event) -> None:
    msg = """
The Agent's Playground is a real-time desktop simulation environment.
Copyright 2023 Samuel Holloway. 
All rights reserved.
"""
    about_dialog = wx.MessageDialog(
      parent = self, 
      message = msg,
      caption = "About Me", 
      style = wx.OK | wx.ICON_INFORMATION
    )
    about_dialog.ShowModal()
    about_dialog.Destroy()

  def _handle_preferences(self, event) -> None:
    pref_dialog = wx.MessageDialog(
      parent = self, 
      message = "TODO",
      caption = "Preferences", 
      style = wx.OK | wx.ICON_INFORMATION
    )
    pref_dialog.ShowModal()
    pref_dialog.Destroy()