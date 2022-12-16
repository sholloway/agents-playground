from abc import ABC, abstractmethod

from agents_playground.terminal.keyboard.types import KeyCode

class KeyHandlerException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class KeyHandler(ABC):
  @abstractmethod
  def match(self, key_code: KeyCode) -> bool:
    """Determine if the handler is a match for the key code."""

  @abstractmethod
  def handle(self, key_code: KeyCode) -> str | None:
    """Processes the key code and returns the corresponding string value."""
