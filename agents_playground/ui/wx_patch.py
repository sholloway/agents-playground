"""
There seems to be a bug in the wxPython binding for WGPU. 
This module patches the implementation of WxWgpuWindow._request_draw
to not have a time to render of 0. Additionally the value must be a float.

To use, import WxWgpuWindow or WgpuWidget from this module rather 
than wgpu.gui.wx.
"""
import wx 
from wgpu.gui.wx import WxWgpuWindow, WgpuWidget

def _request_draw(self):
	"""Patch version of _request_draw"""
	if not self._request_draw_timer.IsRunning():
		time_to_run: float = self._get_draw_wait_time() * 1000.0
		time_to_run = max(1, time_to_run)
		self._request_draw_timer.Start(int(round(time_to_run)), wx.TIMER_ONE_SHOT)

WxWgpuWindow._request_draw = _request_draw
WgpuWidget = WxWgpuWindow