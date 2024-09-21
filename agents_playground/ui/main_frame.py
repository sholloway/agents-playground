"""
This module is the top level window for the Playground UI.
It leverages wxPython for the UI framework.
"""

from enum import IntEnum, auto
import os
from pathlib import Path
import traceback
from typing import Any

import wx
from wgpu.gui.wx import WgpuWidget

from agents_playground.core.task_driven_simulation import TaskDrivenSimulation
from agents_playground.core.webgpu_landscape_editor import WebGPULandscapeEditor
from agents_playground.fp import MaybeMutator, NothingMutator, SomethingMutator
from agents_playground.loaders import (
    JSONFileLoaderStepException,
    set_search_directories,
)
from agents_playground.projects.project_loader import ProjectLoader, ProjectLoaderError
from agents_playground.simulation.types import SimulationLike
from agents_playground.sys.logger import get_default_logger, log_call
from agents_playground.ui.new_sim_frame import NewSimFrame

# Setup logging.
logger = get_default_logger()

# wgpu.logger.setLevel("DEBUG")
# rootLogger = logging.getLogger()
# consoleHandler = logging.StreamHandler()
# rootLogger.addHandler(consoleHandler)


class SimMenuItems(IntEnum):
    NEW_SIM = auto()
    OPEN_SIM = auto()
    NEW_LANDSCAPE = auto()
    OPEN_LANDSCAPE = auto()


class LandscapeEditorModes(IntEnum):
    NEW_LANDSCAPE = auto()
    EDIT_LANDSCAPE = auto()


class MainFrame(wx.Frame):
    @log_call
    def __init__(self, sim_path: str | None = None) -> None:
        """
        Create a new Simulation Frame.

        Args
          - sim_path: The path to a simulation to run.
        """
        super().__init__(None, title="The Agent's Playground")
        self._build_ui()
        self._active_simulation: MaybeMutator[SimulationLike] = NothingMutator()
        self._active_landscape: MaybeMutator[WebGPULandscapeEditor] = NothingMutator()
        if sim_path:
            self._launch_simulation(sim_path)

        self.Show()

    def _build_ui(self) -> None:
        self.SetSize(1600, 900)
        self._build_menu_bar()
        # TODO: After a sim Launches: Add Layers Menu, Buttons: Start/Stop, Toggle Fullscreen, Utility
        self._build_primary_canvas()
        self._build_status_bar()
        # self.Bind(wx.EVT_SIZE, self._handle_frame_resize)
        # self.Bind(wx.EVT_IDLE, self._handle_window_idle)
        self.Bind(wx.EVT_CLOSE, self._handle_close)

    def _build_menu_bar(self) -> None:
        """Construct the top level menu bar."""
        self.menu_bar = wx.MenuBar()

        # Build the File Menu
        # Menu: File -> New | Open
        self.file_menu = wx.Menu()
        self.file_menu.Append(
            id=SimMenuItems.NEW_SIM,
            item="New Simulation...",
            helpString="Create a new simulation project.",
        )
        self.file_menu.Append(
            id=SimMenuItems.OPEN_SIM,
            item="Open Simulation...",
            helpString="Open an existing simulation project.",
        )
        self.file_menu.AppendSeparator()
        self.file_menu.Append(
            id=SimMenuItems.NEW_LANDSCAPE,
            item="New Landscape...",
            helpString="Create a new landscape.",
        )
        self.file_menu.Append(
            id=SimMenuItems.OPEN_LANDSCAPE,
            item="Open Landscape...",
            helpString="Open an existing landscape.",
        )
        self.file_menu.Append(
            id=wx.ID_PREFERENCES,
            item="&Preferences",
            helpString="Set the Playground preferences.",
        )  # Note: On the Mac this displays on the App Menu.

        # Build the Help Menu
        self.help_menu = wx.Menu()
        self.help_menu.Append(
            id=wx.ID_ABOUT, item="&About MyApp"
        )  # Note: On the Mac this displays on the App Menu.

        # Add the menus to the menu bar.
        self.menu_bar.Append(self.file_menu, "&File")
        self.menu_bar.Append(self.help_menu, "&Help")

        self.SetMenuBar(self.menu_bar)

        self.Bind(wx.EVT_MENU, self._handle_new_sim, id=SimMenuItems.NEW_SIM)
        self.Bind(wx.EVT_MENU, self._handle_open_sim, id=SimMenuItems.OPEN_SIM)
        self.Bind(
            wx.EVT_MENU, self._handle_new_landscape, id=SimMenuItems.NEW_LANDSCAPE
        )
        self.Bind(
            wx.EVT_MENU, self._handle_open_landscape, id=SimMenuItems.OPEN_LANDSCAPE
        )
        self.Bind(wx.EVT_MENU, self._handle_about_request, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self._handle_preferences, id=wx.ID_PREFERENCES)

    def _build_primary_canvas(self) -> None:
        top_level_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self)
        self.panel.SetSizer(top_level_sizer)
        self.canvas = WgpuWidget(self.panel, max_fps=1000, vsync=False)
        top_level_sizer.Add(self.canvas, proportion=1, flag=wx.EXPAND)

    def _build_status_bar(self) -> None:
        self.CreateStatusBar()

    def _handle_new_sim(self, event) -> None:
        """
        Create a new simulation.
        """
        nsf = NewSimFrame(parent=self)
        nsf.CenterOnParent()
        nsf.Show()

    def _handle_open_sim(self, _: wx.Event) -> None:
        """
        Open an existing simulation.
        """
        sp: wx.StandardPaths = wx.StandardPaths.Get()

        sim_picker = wx.DirDialog(
            parent=self,
            message="Open a Simulation",
            defaultPath=sp.GetDocumentsDir(),
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR,
        )

        if sim_picker.ShowModal() == wx.ID_OK:
            sim_path = sim_picker.GetPath()
            self._launch_simulation(sim_path)

        sim_picker.Destroy()

    def _handle_new_landscape(self, _: wx.Event) -> None:
        """
        Select a directory to create a landscape in and launch the Landscape editor.
        """
        sp: wx.StandardPaths = wx.StandardPaths.Get()

        new_file_picker = wx.FileDialog(
            self,
            message="Create landscape as ...",
            defaultDir=sp.GetDocumentsDir(),
            defaultFile="landscape.json",
            wildcard="Landscape file (*.json)|*.json|",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )

        if new_file_picker.ShowModal() == wx.ID_OK:
            self._launch_landscape_editor(
                landscape_path=new_file_picker.GetPath(),
                mode=LandscapeEditorModes.NEW_LANDSCAPE,
            )

        new_file_picker.Destroy()

    def _handle_open_landscape(self, _: wx.Event) -> None:
        """
        Select an existing Landscape JSON file and open it in the Landscape editor.
        """
        print("Open Landscape")

    def _handle_frame_resize(self, event: wx.Event) -> None:
        """
        Current Focus: Correctly handle the frame resizing.
        - Recalculate the camera's aspect ratio based on the canvas' size.
        - Bind the new camera to the rendering pipeline.
        - Request a redraw.
        """
        if self._active_simulation.is_something():
            self._active_simulation.unwrap().handle_aspect_ratio_change(self.canvas)
        else:
            print("No active simulation")

        event.Skip(True)

    def _handle_window_idle(self, event: wx.Event) -> None:
        print(event)
        print(f"Panel GetSize: {self.panel.GetSize()}")
        print(f"Canvas GetSize: {self.canvas.GetSize()}")
        print(f"Canvas get_physical_size: self.canvas.get_physical_size()")

    @log_call
    def _launch_simulation(self, sim_path) -> None:
        """
        Attempts to load a simulation project into memory and run it.
        """
        try:
            module_name = os.path.basename(sim_path)
            project_path = os.path.join(sim_path, module_name)
            # 1. Load the Python components of the simulation.
            pl = ProjectLoader()
            pl.validate(module_name, project_path)
            pl.load(module_name, project_path)

            # 2. Load the JSON configuration for the simulation
            scene_file: str = os.path.join(project_path, "scene.json")
            simulation: SimulationLike = self._build_simulation(
                scene_file, project_path
            )

            # 3. Run the simulation
            self._active_simulation = SomethingMutator[SimulationLike](simulation)
            self._active_simulation.mutate(
                [("bind_event_listeners", self.canvas), ("launch",)]
            )
        except (ProjectLoaderError, TypeError, JSONFileLoaderStepException) as e:
            error_msg = (
                "There was an error while trying to load a simulation.\n",
                "The error was.\n",
                str(e),
                "\n\n",
                traceback.format_exc(),
            )
            error_dialog = wx.GenericMessageDialog(
                parent=self,
                message="".join(error_msg),
                caption="Project Validation Error",
                style=wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE,
            )
            if error_dialog.ShowModal():
                error_dialog.Destroy()
        except Exception as e:
            traceback.print_exception(e)
            error_msg = (
                "There was an error while trying to load a simulation.\n",
                "The error was.\n",
                str(e),
                "\n\n",
                traceback.format_exc(),
            )
            error_dialog = wx.GenericMessageDialog(
                parent=self,
                message="".join(error_msg),
                caption="Project Validation Error",
                style=wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE,
            )
            if error_dialog.ShowModal():
                error_dialog.Destroy()

    def _build_simulation(self, scene_file: Any, project_path: str) -> SimulationLike:
        set_search_directories(
            [
                project_path,  # First search in the project's directory.
                str(Path.cwd()),  # Then search in current working directory.
            ]
        )

        # TODO: Delete this after the TaskDrivenSimulation is done.
        # return WebGPUSimulation(
        #     parent=self,
        #     canvas=self.canvas,
        #     scene_file=scene_file,
        #     scene_loader=SceneLoader(),
        # )
        return TaskDrivenSimulation(canvas=self.canvas, scene_file=scene_file)

    def _launch_landscape_editor(
        self, landscape_path: str, mode: LandscapeEditorModes
    ) -> None:
        print(landscape_path)
        self._active_landscape = SomethingMutator[WebGPULandscapeEditor](
            WebGPULandscapeEditor(
                parent=self, canvas=self.canvas, landscape_path=landscape_path
            )
        )
        self._active_landscape.mutate(
            [("attach", self), ("bind_event_listeners", self.canvas), ("launch",)]
        )

    def update(self, msg: str) -> None:
        """Receives a notification message from an observable object."""
        # if msg == SimulationEvents.WINDOW_CLOSED.value:
        #     self._active_simulation.mutate([("detach",)])
        pass

    def _handle_about_request(self, event: wx.Event) -> None:
        # TODO: Pull into a config file.
        msg = """
The Agent's Playground is a real-time desktop simulation environment.
Copyright 2023 Samuel Holloway.
All rights reserved.
"""
        about_dialog = wx.MessageDialog(
            parent=self,
            message=msg,
            caption="About Me",
            style=wx.OK | wx.ICON_INFORMATION,
        )
        about_dialog.ShowModal()
        about_dialog.Destroy()

    def _handle_preferences(self, event: wx.Event) -> None:
        pref_dialog = wx.MessageDialog(
            parent=self,
            message="TODO",
            caption="Preferences",
            style=wx.OK | wx.ICON_INFORMATION,
        )
        pref_dialog.ShowModal()
        pref_dialog.Destroy()

    @log_call
    def _handle_close(self, _: wx.Event) -> None:
        logger.info("Main Frame: It's closing time!")
        if self._active_simulation.is_something():
            self._active_simulation.mutate([("shutdown",)])
        self.Destroy()
        # Calling to skip the wxPython cleanup and resulting segfault
        # https://github.com/wxWidgets/Phoenix/issues/2455
        # https://docs.python.org/3/library/os.html#os._exit
        os._exit(os.EX_OK)
