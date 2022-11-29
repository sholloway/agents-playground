from collections import deque
from typing import Deque, List

SCROLL_BACK_BUFFER_MAX_LENGTH = 10
class TerminalBuffer():
  """Displays the previous commands and their output."""
  def __init__(self) -> None:
    # Will need to migrate to an abstract data time if I want to colorize the output
    # for errors and prompts.s
    self._scroll_back_buffer: Deque[str] = deque([], maxlen=SCROLL_BACK_BUFFER_MAX_LENGTH)
    self._active_prompt: str = ''

  
  def append(self, char: str) -> None:
    self._active_prompt = self._active_prompt + char

  def append_output(self, output: str) -> None:
    self._scroll_back_buffer.append(output)

  def remove(self, length: int) -> None:
    self._active_prompt = self._active_prompt[:-length]

  def clear_prompt(self) -> None:
    self._active_prompt = ''

  @property
  def active_prompt(self) -> str:
    return self._active_prompt

  @property
  def scroll_back_buffer(self) -> List[str]:
    return list(self._scroll_back_buffer)