import re
import wx

from agents_playground.ui.components.input_error_popup import InputErrorPopup
from agents_playground.ui.validators import keycode_to_value


class PatternValidator(wx.Validator):
    def __init__(
        self,
        pattern: str,
        error_msg: str,
        background_color: tuple[int, ...],
        foreground_color: tuple[int, ...],
    ) -> None:
        super().__init__()
        self._pattern = pattern
        self._error_msg = error_msg
        self._caps_lock_key_down: bool = False
        self._original_background_color = background_color
        self._original_text_color = foreground_color
        self.Bind(wx.EVT_KEY_DOWN, self._handle_key_down)
        self.Bind(wx.EVT_KEY_UP, self._handle_key_up)
        self.Bind(wx.EVT_CHAR, self._handle_on_char)

    def Clone(self):
        return PatternValidator(
            self._pattern,
            self._error_msg,
            self._original_background_color,
            self._original_text_color,
        )

    def _handle_on_char(self, event: wx.KeyEvent) -> None:
        """Only allow proper characters when typing."""
        key_code: int = event.GetKeyCode()
        key_value: str = keycode_to_value(
            key_code, event.ShiftDown(), self._caps_lock_key_down
        )
        if key_code == wx.WXK_DELETE or re.match(self._pattern, key_value) is not None:
            event.Skip()
        return

    def _handle_key_down(self, event: wx.KeyEvent) -> None:
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_CAPITAL:
            self._caps_lock_key_down = True
        event.Skip()
        return

    def _handle_key_up(self, event: wx.KeyEvent) -> None:
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_CAPITAL:
            self._caps_lock_key_down = False
        event.Skip()
        return

    def Validate(self, win):
        """Called when the parent component does a self.Validate()"""
        component = self.GetWindow()
        value = component.GetValue()
        match = re.match(self._pattern, value)
        if match:
            component.SetBackgroundColour(self._original_background_color)
            component.SetForegroundColour(self._original_text_color)
            component.Refresh()
        else:
            error_popup = InputErrorPopup(
                parent=component,
                style=wx.NO_BORDER,
                error_msg=self._error_msg,
                font=component.GetFont(),
            )

            component_pos = component.ClientToScreen((0, 0))
            component_size = component.GetSize()
            error_popup.Position(component_pos, (0, component_size[1]))
            error_popup.Popup()

            component.SetForegroundColour("black")
            component.SetBackgroundColour("pink")
            component.SetFocus()
            component.Refresh()
        return match is not None

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True
