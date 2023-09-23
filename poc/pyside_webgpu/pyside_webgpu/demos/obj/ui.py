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

    camera_pos_label = wx.StaticText(panel, label='Camera Position (X,Y,Z)')
    camera_right_label = wx.StaticText(panel, label='Right Axis (I,J, K)')
    camera_up_label = wx.StaticText(panel, label='Up Axis (I,J, K)')
    camera_facing_label = wx.StaticText(panel, label='Facing Axis (I,J, K)')
    
    self.slider_x = self._build_unit_slider('CAMERA_POS_X', panel, self._handle_slider_changed)
    self.slider_y = self._build_unit_slider('CAMERA_POS_Y', panel, self._handle_slider_changed)
    self.slider_z = self._build_unit_slider('CAMERA_POS_Z', panel, self._handle_slider_changed)
    
    self.cam_right_slider_i = self._build_unit_slider('CAMERA_RIGHT_I', panel, self._handle_slider_changed)
    self.cam_right_slider_j = self._build_unit_slider('CAMERA_RIGHT_J', panel, self._handle_slider_changed)
    self.cam_right_slider_k = self._build_unit_slider('CAMERA_RIGHT_K', panel, self._handle_slider_changed)
    

    self.canvas = WgpuWidget(panel)
    self.canvas.SetMinSize((640, 640))

    top_level_sizer = wx.BoxSizer(wx.VERTICAL)
    top_level_sizer.Add((1,20))

    row_one_sizer = wx.BoxSizer(wx.HORIZONTAL)
    row_two_sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    top_level_sizer.Add(camera_pos_label, 0, wx.LEFT, 20)
    row_one_sizer.AddMany([
      (self.slider_x, 0, wx.LEFT, 20),
      (self.slider_y, 0, wx.LEFT, 20),
      (self.slider_z, 0, wx.LEFT, 20)
    ])
    top_level_sizer.Add(row_one_sizer, 0, wx.EXPAND)

    top_level_sizer.Add(camera_right_label, 0, wx.LEFT, 20)
    row_two_sizer.AddMany([
      (self.cam_right_slider_i, 0, wx.LEFT, 20),
      (self.cam_right_slider_j, 0, wx.LEFT, 20),
      (self.cam_right_slider_k, 0, wx.LEFT, 20)
    ])
    top_level_sizer.Add(row_two_sizer, 0, wx.EXPAND)
    

    top_level_sizer.Add(camera_up_label, 0, wx.LEFT, 20)
    top_level_sizer.Add(camera_facing_label, 0, wx.LEFT, 20)

    top_level_sizer.Add((1,10))
    top_level_sizer.Add(self.canvas, 0 )
    
    # top_level_sizer.Add(self.slider, 0, wx.LEFT, 20)
    # top_level_sizer.Add((1,10))
    panel.SetSizer(top_level_sizer)

    # self.SetAutoLayout(True)
    
    self.Show()

  def _build_unit_slider(
    self, 
    name: str, 
    parent: wx.Window,
    change_event_handler: Callable
  ) -> UnitSlider:
    slider = UnitSlider(
      parent, 
      id       = -1,
      name     = name,
      value    = 0,
      minValue = -100,
      maxValue = 100,
      size     = (250, -1),
      style    = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
    )
    slider.Bind(wx.EVT_SLIDER, change_event_handler)
    return slider

  def set_ui_update_handler(self, update_camera: Callable) -> None:
    self._update_camera = update_camera

  def set_update_uniforms_handler(self, update_uniforms: Callable) -> None:
    self._update_uniforms = update_uniforms

  def _handle_slider_changed(self, event) -> None:
    obj = event.GetEventObject() 
    
    next_x: float | None = None
    next_y: float | None = None
    next_z: float | None = None
    
    next_cam_right_i: float | None = None
    next_cam_right_j: float | None = None
    next_cam_right_k: float | None = None
    
    match obj.GetName():
      case 'CAMERA_POS_X':
        next_x = float(obj.GetValue())
      case 'CAMERA_POS_Y':
        next_y = float(obj.GetValue())
      case 'CAMERA_POS_Z':
        next_z = float(obj.GetValue())
      case 'CAMERA_RIGHT_I':
        next_cam_right_i = float(obj.GetValue())
      case 'CAMERA_RIGHT_J':
        next_cam_right_j = float(obj.GetValue())
      case 'CAMERA_RIGHT_K':
        next_cam_right_k = float(obj.GetValue())
      
    self._update_camera(next_x, next_y, next_z, 
                        next_cam_right_i, next_cam_right_j, next_cam_right_k)
    self._update_uniforms()
    self.canvas.request_draw()