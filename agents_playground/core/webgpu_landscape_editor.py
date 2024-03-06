
import wx
import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.core.observe import Observable

class WebGPULandscapeEditor(Observable):
  def __init__(
    self, 
    parent: wx.Window,
    canvas: WgpuWidget,
    landscape_path: str, 
  ) -> None:
    super().__init__()
    self._parent_window = parent
    self._canvas = canvas
    self._landscape_path = landscape_path

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""
    # This is a holder over from the DearPyGUI based design. Skipping for the moment.
    pass

  def bind_event_listeners(self, frame: wx.Panel) -> None:
    """
    Given a panel, binds event listeners.
    """
    pass # No event listens for the moment...


  def launch(self) -> None:
    """
    Starts the simulation running.
    """
    print('Boga Boga')