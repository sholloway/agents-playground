"""
This module is the top level window for the Playground UI.
It leverages wxPython for the UI framework.
"""

from enum import IntEnum
import logging
import os
from typing import Any
from agents_playground.fp import (
  MaybeMutator, 
  NothingMutator, 
  SomethingMutator 
)

import wx
import wgpu
import wgpu.backends.wgpu_native

from agents_playground.core.observe import Observer
from agents_playground.core.simulation import Simulation
from agents_playground.core.webgpu_simulation import WebGPUSimulation
from agents_playground.project.project_loader_error import ProjectLoaderError
from agents_playground.project.rules.project_loader import ProjectLoader
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.simulation.sim_events import SimulationEvents
from agents_playground.sys.logger import get_default_logger

from agents_playground.ui.wx_patch import WgpuWidget 
# Setup logging.
logger = get_default_logger()
# wgpu.logger.setLevel("DEBUG")
# rootLogger = logging.getLogger()
# consoleHandler = logging.StreamHandler()
# rootLogger.addHandler(consoleHandler)
# ENABLE_WGPU_TRACING = True


class SimMenuItems(IntEnum):
  NEW_SIM = 1000
  OPEN_SIM = 1001

class SimFrame(wx.Frame):
  def __init__(self, sim_path: str | None = None) -> None:
    """
    Create a new Simulation Frame.

    Args
      - sim_path: The path to a simulation to run.
    """
    super().__init__(None, title="The Agent's Playground")
    self._build_ui()
    self._active_simulation : MaybeMutator[WebGPUSimulation] = NothingMutator()
    if sim_path:
      self._launch_simulation(sim_path)

    self.Show()

  def _build_ui(self) -> None:
    self.SetSize(800, 950)
    self._build_menu_bar()
    # TODO: After a sim Launches: Add Layers Menu, Buttons: Start/Stop, Toggle Fullscreen, Utility
    self._build_primary_canvas()
    self._build_status_bar()
    # self.Bind(wx.EVT_SIZE, self._handle_frame_resize)
    # self.Bind(wx.EVT_IDLE, self._handle_window_idle)

  def _build_menu_bar(self) -> None:
    """Construct the top level menu bar."""
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

    # Add the menus to the menu bar.
    self.menu_bar.Append(self.file_menu, "&File")
    self.menu_bar.Append(self.help_menu, "&Help")

    self.SetMenuBar(self.menu_bar)

    self.Bind(wx.EVT_MENU, self._handle_new_sim, id=SimMenuItems.NEW_SIM)
    self.Bind(wx.EVT_MENU, self._handle_open_sim, id=SimMenuItems.OPEN_SIM)
    self.Bind(wx.EVT_MENU, self._handle_about_request, id=wx.ID_ABOUT) 
    self.Bind(wx.EVT_MENU, self._handle_preferences, id=wx.ID_PREFERENCES) 

  def _build_primary_canvas(self) -> None:
    top_level_sizer = wx.BoxSizer(wx.VERTICAL)
    self.panel = wx.Panel(self)
    self.panel.SetSizer(top_level_sizer)
    self.canvas = WgpuWidget(self.panel)
    top_level_sizer.Add(self.canvas, proportion = 1, flag = wx.EXPAND) 
    
  def _build_status_bar(self) -> None:
    self.CreateStatusBar()

  def _handle_new_sim(self, event) -> None:
    print(f'Clicked New: {type(event)}, {event}')

  def _handle_open_sim(self, event) -> None:
    """
    Open an existing simulation.
    """
    print(f'Clicked Open: {type(event)}, {event}')
    sp: wx.StandardPaths = wx.StandardPaths.Get()
    
    sim_picker = wx.DirDialog(
      parent=self,
      message = "Open a Simulation",
      defaultPath=sp.GetDocumentsDir(),
      style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR
    )

    if sim_picker.ShowModal() == wx.ID_OK:
      sim_path = sim_picker.GetPath()
      self._launch_simulation(sim_path)

    sim_picker.Destroy()

  def _handle_frame_resize(self, event: wx.Event) -> None:
    """
    Current Focus: Correctly handle the frame resizing.
    - Recalculate the camera's aspect ratio based on the canvas' size.
    - Bind the new camera to the rendering pipeline.
    - Request a redraw.
    """
    if self._active_simulation.is_something():
      print(event)
      self._active_simulation.unwrap().handle_aspect_ratio_change(self.canvas)
    else:
      print("No active simulation")

    event.Skip(True) #

  def _handle_window_idle(self, event: wx.Event) -> None:
    print(event)
    print(f'Panel GetSize: {self.panel.GetSize()}')
    print(f"Canvas GetSize: {self.canvas.GetSize()}")
    print(f"Canvas get_physical_size: self.canvas.get_physical_size()")

  def _launch_simulation(self, sim_path) -> None:
    module_name = os.path.basename(sim_path)
    project_path = os.path.join(sim_path, module_name)
    pl = ProjectLoader()
    try:
      pl.validate(module_name, project_path)   
      pl.load_or_reload(module_name, project_path)
      scene_file: str = os.path.join(project_path, 'scene.toml')
      self._active_simulation = SomethingMutator[WebGPUSimulation](self._build_simulation(scene_file))
      self._active_simulation.mutate([('attach', self), ('launch',)])
    except ProjectLoaderError as e:
      error_dialog = wx.MessageDialog(
        parent = self, 
        message = repr(e),
        caption = 'Project Validation Error', 
        style = wx.OK | wx.ICON_INFORMATION
      )
      error_dialog.ShowModal()
      error_dialog.Destroy()

  def _build_simulation(self, scene_file: Any) -> WebGPUSimulation:
    return WebGPUSimulation(
      parent = self, 
      canvas = self.canvas,
      scene_file = scene_file, 
      scene_reader = SceneReader()
    ) 
  
  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""   
    logger.info('PlaygroundApp: Update message received.')
    if msg == SimulationEvents.WINDOW_CLOSED.value:
      self._active_simulation.mutate([('detach',)])
    
  
  def _handle_about_request(self, event) -> None:
    # TODO: Pull into a config file.
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