"""
This module provides the orchestration for the top level window for the
Playground UI.
"""

import wx

from agents_playground.sys.logger import log_call
from agents_playground.ui.main_frame import MainFrame


class Playground(wx.App):
    @log_call
    def __init__(
        self,
        redirect_output: bool = False,
        redirect_filename: str | None = None,
        auto_launch_sim_path: str | None = None,
    ):
        """
        Creates a new playground application.

        Args
          - redirect_output: Should sys.stdout and sys.stderr be redirected?
          - redirect_filename: The name of a file to redirect output to, if redirect is True.
          - auto_launch_sim_path: The path to a Simulation to auto-launch.
        """
        self._auto_launch_sim_path = auto_launch_sim_path
        super().__init__(
            redirect=redirect_output,
            filename=redirect_filename,
            useBestVisual=False,
            clearSigInt=False,  # Should SIGINT be cleared? Enable Ctrl-C to kill the app in the terminal.
        )
        self.Bind(wx.EVT_ACTIVATE_APP, self._on_activate)

    def _on_activate(self, event):
        # Handle events when the app is asked to activate by some other process.
        if event.GetActive():
            self._bring_window_to_front()
        event.Skip()

    def _bring_window_to_front(self):
        try:
            # Note: It's possible for this event to come when the frame is closed.
            self.GetTopWindow().Raise()
        except Exception:
            pass

    def OnInit(self) -> bool:
        """wx.App lifecycle method."""
        self.sim_frame = MainFrame(sim_path=self._auto_launch_sim_path)
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

    def MacPrintFile(self, file_path: str) -> None:
        pass
