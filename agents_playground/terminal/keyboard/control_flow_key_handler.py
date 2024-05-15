import dearpygui.dearpygui as dpg
from agents_playground.terminal.keyboard.key_handler import (
    KeyHandler,
    KeyHandlerException,
)
from agents_playground.terminal.keyboard.types import KeyCode

TERM_SPACES_PER_TAB = 2


class ControlFlowKeyHandler(KeyHandler):
    def __init__(self) -> None:
        super().__init__()
        self._keys = {256, 257, 258, 259}

    def match(self, key_code: KeyCode) -> bool:
        """Determine if the handler is a match for the key code."""
        return key_code in self._keys

    def handle(self, key_code: KeyCode) -> str | None:
        """Processes the key code and returns the corresponding string value."""
        match key_code:
            case 256:  # ESC
                return "ESC"
            case 258:  # Tab
                return "\t".expandtabs(TERM_SPACES_PER_TAB)
            case 259:  # Back/Delete/Clear
                return "\b"
            case 257 if dpg.is_key_down(key=dpg.mvKey_Shift):  # Enter/Return + Shift
                return "RUN_CODE"
            case 257:  # Enter/Return
                return "NEW_LINE"
        raise KeyHandlerException(
            f"ControlFlowKeyHandler could not process key code {key_code}"
        )
