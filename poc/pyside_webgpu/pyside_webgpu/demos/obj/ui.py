from typing import Callable
import wx
from pyside_webgpu.demos.wx.wx_patch import WgpuWidget

class UnitSlider(wx.Slider):
  def __init__(self, *args, **kw):
    super().__init__(*args, **kw)

  def GetValue(self):
    return (float(wx.Slider.GetValue(self)))/self.GetMax()
  
class AppWindow(wx.Frame):
  """Create a simple window with a canvas that can be rendered in."""
  def __init__(self) -> None:
    super().__init__(None, title="Obj Model Loader")
    self.SetSize(800, 950)
    
    panel = wx.Panel(self)

    """
    Use slides to control the position of the camera.
    wx.SpinButton or SpinCtrl might also be useful.
    """

    camera_pos_label = wx.StaticText(panel, label='Camera Position')
    camera_pos_x_label = wx.StaticText(panel, label='X-axis')
    camera_pos_y_label = wx.StaticText(panel, label='Y-axis')
    camera_pos_z_label = wx.StaticText(panel, label='Z-axis')
    
    self.slider_x = UnitSlider(
      panel, 
      id       = -1,
      name     = 'CAMERA_POS_X',
      value    = 0,
      minValue = -100,
      maxValue = 100,
      size     = (250, -1),
      style    = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
    )

    self.slider_y = UnitSlider(
      panel, 
      id       = -1,
      name     = 'CAMERA_POS_Y',
      value    = 0,
      minValue = -100,
      maxValue = 100,
      size     = (250, -1),
      style    = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
    )

    self.slider_z = UnitSlider(
      panel, 
      id       = -1,
      name     = 'CAMERA_POS_Z',
      value    = 0,
      minValue = -100,
      maxValue = 100,
      size     = (250, -1),
      style    = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
    )

    self.slider_x.Bind(wx.EVT_SLIDER, self._handle_slider_changed)
    self.slider_y.Bind(wx.EVT_SLIDER, self._handle_slider_changed)
    self.slider_z.Bind(wx.EVT_SLIDER, self._handle_slider_changed)

    self.canvas = WgpuWidget(panel)
    self.canvas.SetMinSize((640, 640))

    top_level_sizer = wx.BoxSizer(wx.VERTICAL)
    top_level_sizer.Add((1,20))
    top_level_sizer.Add(camera_pos_label, 0, wx.LEFT, 20)
    top_level_sizer.Add(camera_pos_x_label, 0, wx.LEFT, 20)
    top_level_sizer.Add(self.slider_x, 0, wx.LEFT, 20)
    top_level_sizer.Add(camera_pos_y_label, 0, wx.LEFT, 20)
    top_level_sizer.Add(self.slider_y, 0, wx.LEFT, 20)
    top_level_sizer.Add(camera_pos_z_label, 0, wx.LEFT, 20)
    top_level_sizer.Add(self.slider_z, 0, wx.LEFT, 20)
    top_level_sizer.Add(self.canvas, 0 )
    
    top_level_sizer.Add((1,10))
    # top_level_sizer.Add(self.slider, 0, wx.LEFT, 20)
    # top_level_sizer.Add((1,10))
    panel.SetSizer(top_level_sizer)

    # self.SetAutoLayout(True)
    
    self.Show()

  def set_ui_update_handler(self, update_camera: Callable) -> None:
    self._update_camera = update_camera

  def set_update_uniforms_handler(self, update_uniforms: Callable) -> None:
    self._update_uniforms = update_uniforms

  def _handle_slider_changed(self, event) -> None:
    obj = event.GetEventObject() 
    
    next_x: float | None = None
    next_y: float | None = None
    next_z: float | None = None

    match obj.GetName():
      case 'CAMERA_POS_X':
        next_x = float(obj.GetValue())
      case 'CAMERA_POS_Y':
        next_y = float(obj.GetValue())
      case 'CAMERA_POS_Z':
        next_z = float(obj.GetValue())

    self._update_camera(next_x, next_y, next_z)
    self._update_uniforms()
    self.canvas.request_draw()