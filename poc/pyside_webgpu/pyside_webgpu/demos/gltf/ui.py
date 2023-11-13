import wx
from pyside_webgpu.demos.wx.wx_patch import WgpuWidget

class AppWindow(wx.Frame):
  """Create a simple window with a canvas that can be rendered in."""
  def __init__(self) -> None:
    super().__init__(None, title="Naive glTF Scene Loader")
    self.SetSize(640, 480)
    self.canvas = WgpuWidget(self)
    self.Show()
  