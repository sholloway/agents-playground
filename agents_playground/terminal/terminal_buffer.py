from collections import deque
from typing import Deque, List

SCROLL_BACK_BUFFER_MAX_LENGTH = 10
HISTORY_BUFFER_MAX_LENGTH = 50
class TerminalBuffer():
  """Displays the previous commands and their output."""
  def __init__(self) -> None:
    self._scroll_back_buffer: Deque[str] = deque([], maxlen=SCROLL_BACK_BUFFER_MAX_LENGTH)
    self._history_buffer: Deque[str] = deque([], maxlen=HISTORY_BUFFER_MAX_LENGTH)
    self._active_prompt: str = ''

  def _remember(self, output: str) -> None:
    """Appends the provided output to the history buffer."""
    self._history_buffer.append(output)
  
  def append(self, char: str) -> None:
    """Add a character to the active prompt."""
    self._active_prompt = self._active_prompt + char

  def append_output(self, output: str | List[str], remember: bool = True) -> None:
    """Add a line(s) to the scroll back buffer."""
    if isinstance(output, str):
      self._scroll_back_buffer.append(output)
      if remember:
        self._remember(output)
    elif isinstance(output, list):
      self._scroll_back_buffer.extend(output)

  def remove(self, length: int) -> None:
    """Remove N number of characters from the right of the active prompt."""
    self._active_prompt = self._active_prompt[:-length]

  def clear_prompt(self) -> None:
    """Empties the prompt."""
    self._active_prompt = ''

  def clear(self) -> None:
    """Empties the buffer and active prompt."""
    self._scroll_back_buffer.clear()
    self.clear_prompt()

  @property
  def active_prompt(self) -> str:
    return self._active_prompt

  @property
  def scroll_back_buffer(self) -> List[str]:
    return list(self._scroll_back_buffer)
  
  def history(self) -> List[str]:
    """Returns a copy of the history buffer."""
    return list(self._history_buffer)