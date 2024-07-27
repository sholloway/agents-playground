import wx


class InputErrorPopup(wx.PopupTransientWindow):
    """
    Dynamically creates a popup pane that displays an error adjacent to the
    parent component.

    **Example Use**
    error_popup = InputErrorPopup(
      parent    = component,
      style     = wx.NO_BORDER,
      error_msg = self._error_msg,
      font      = component.GetFont()
    )

    component_pos = component.ClientToScreen( (0,0) )
    component_size =  component.GetSize()
    error_popup.Position(component_pos, (0, component_size[1]))
    error_popup.Popup()

    """

    def __init__(self, parent: wx.Window, style: int, error_msg: str, font: wx.Font):
        super().__init__(parent, style)
        self._panel = wx.Panel(self)
        self._panel.SetBackgroundColour("#FFB6C1")

        error_label = wx.StaticText(self._panel, label="Input Error")
        error_msg_component = wx.StaticText(self._panel, label=error_msg)

        error_label.SetFont(font.Bold())
        error_label.SetForegroundColour("black")
        error_msg_component.SetFont(font)
        error_msg_component.SetForegroundColour("black")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(error_label, flag=wx.ALL, border=5)
        sizer.Add(error_msg_component, flag=wx.ALL, border=5)

        self._panel.SetSizer(sizer)
        sizer.Fit(self._panel)
        sizer.Fit(self)
        self.Layout()
