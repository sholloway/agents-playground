import wx
from pyside_webgpu.demos.wx.wx_patch import WgpuWidget

class AppWindow(wx.Frame):
  """Create a simple window with a canvas that can be rendered in."""
  def __init__(self) -> None:
    super().__init__(None, title="WX App")
    self.SetSize(640, 480)
    self.canvas = WgpuWidget()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(self.canvas, 0, wx.EXPAND)
    self.SetSizer(sizer)
    self.Show()
  