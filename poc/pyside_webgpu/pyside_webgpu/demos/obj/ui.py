import wx
from pyside_webgpu.demos.wx.wx_patch import WgpuWidget

class AppWindow(wx.Frame):
  """Create a simple window with a canvas that can be rendered in."""
  def __init__(self) -> None:
    super().__init__(None, title="Obj Model Loader")
    self.SetSize(800, 800)
    
    panel = wx.Panel(self)

    """
    Use slides to control the position of the camera.
    wx.SpinButton or SpinCtrl might also be useful.
    """

    self.camera_pos_label = wx.StaticText(
      panel, 
      id     = -1, 
      label  = 'Camera Position'
    )
    self.slider = wx.Slider(
      panel, 
      id       = -1,
      value    = 0,
      minValue = -1,
      maxValue = 1,
      size     = (250, -1),
      style    = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
    )

    self.canvas = WgpuWidget(panel)
    self.canvas.SetMinSize((640, 640))

    top_level_sizer = wx.BoxSizer(wx.VERTICAL)
    top_level_sizer.Add((1,20))
    top_level_sizer.Add(self.camera_pos_label, 0, wx.LEFT, 20)
    top_level_sizer.Add((1,10))
    top_level_sizer.Add(self.slider, 0, wx.LEFT, 20)
    top_level_sizer.Add((1,10))
    top_level_sizer.Add(self.canvas, 0 )
    panel.SetSizer(top_level_sizer)

    # self.SetAutoLayout(True)
    
    self.Show()