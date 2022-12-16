"""
Module responsible for listening to key events and converting them to characters.
"""

from agents_playground.terminal.keyboard.types import KeyCode
from agents_playground.terminal.keyboard.alpha_key_handler import AlphaKeyHandler
from agents_playground.terminal.keyboard.arrow_key_handler import ArrowKeyHandler
from agents_playground.terminal.keyboard.control_flow_key_handler import ControlFlowKeyHandler
from agents_playground.terminal.keyboard.numeric_key_handler import NumericKeyHandler
from agents_playground.terminal.keyboard.space_key_handler import SpaceKeyHandler
from agents_playground.terminal.keyboard.symbol_key_handler import SymbolKeyHandler
from agents_playground.terminal.keyboard.unknown_key_handler import UnknownKeyHandler

class KeyInterpreter:
  def __init__(self) -> None:
    self.key_handlers = [
      SpaceKeyHandler(), 
      ArrowKeyHandler(), 
      ControlFlowKeyHandler(),
      AlphaKeyHandler(),
      NumericKeyHandler(),
      SymbolKeyHandler(),
      UnknownKeyHandler()
    ]

  def key_to_char(self, key_code: KeyCode) -> str | None:
    # TODO: Is there a cleaner way of doing this with itertools?
    for handler in self.key_handlers:
      if handler.match(key_code):
        return handler.handle(key_code)