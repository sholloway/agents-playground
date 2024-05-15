import dearpygui.dearpygui as dpg
from agents_playground.terminal.keyboard.key_handler import (
    KeyHandler,
    KeyHandlerException,
)
from agents_playground.terminal.keyboard.types import KeyCode


class NumericKeyHandler(KeyHandler):
    def __init__(self) -> None:
        super().__init__()

    def match(self, key_code: KeyCode) -> bool:
        """Determine if the handler is a match for the key code."""
        return 48 <= key_code and key_code <= 57

    def handle(self, key_code: KeyCode) -> str | None:
        """Processes the key code and returns the corresponding string value."""
        # Use Case: Key Shift + [0-9] -> [!, @, #, $, %, ^, &, *, (,) ]
        if dpg.is_key_down(key=dpg.mvKey_Shift):
            match key_code:
                case 0x30:
                    return ")"
                case 0x31:
                    return "!"
                case 0x32:
                    return "@"
                case 0x33:
                    return "#"
                case 0x34:
                    return "$"
                case 0x35:
                    return "%"
                case 0x36:
                    return "^"
                case 0x37:
                    return "&"
                case 0x38:
                    return "*"
                case 0x39:
                    return "("
                case _:
                    raise KeyHandlerException(
                        f"NumericKeyHandler could not process key code {key_code}"
                    )
        else:
            # Use Case: [0-9] -> [0-9]
            return chr(key_code)
