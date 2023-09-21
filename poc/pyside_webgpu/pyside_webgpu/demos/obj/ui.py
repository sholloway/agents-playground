import wx
from pyside_webgpu.demos.wx.wx_patch import WgpuWidget

class AppWindow(wx.Frame):
  """Create a simple window with a canvas that can be rendered in."""
  def __init__(self) -> None:
    super().__init__(None, title="Obj Model Loader")
    self.SetSize(640, 480)
    

    """
    Use slides to control the position of the camera.
    wx.SpinButton or SpinCtrl might also be useful.
    """
    self.camera_pos_label = wx.StaticText(
      self, 
      id     = -1, 
      label  = 'Camera Position'
    )
    self.slider = wx.Slider(
      self, 
      id       = -1,
      value    = 0,
      minValue = -1,
      maxValue = 1,
      size     = (250, -1),
      style    = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
    )

    self.canvas = WgpuWidget(self)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add((1,20))
    sizer.Add(self.camera_pos_label, 0, wx.LEFT, 20)
    sizer.Add((1,10))
    sizer.Add(self.slider, 0, wx.LEFT, 20)
    sizer.Add((1,10))
    sizer.Add(self.canvas, 0, wx.LEFT, 20)

    self.SetSizer(sizer)
    self.Show()