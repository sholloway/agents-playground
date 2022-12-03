from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, List

SCROLL_BACK_BUFFER_MAX_LENGTH = 10
HISTORY_BUFFER_MAX_LENGTH = 50

class TerminalBufferContent(ABC):
  def __init__(self) -> None:
    pass

  @abstractmethod
  def raw_content(self) -> str:
    """The unformatted buffer content."""

  @abstractmethod
  def format(self) -> None:
    """Responsible for structuring the terminal message."""

class TerminalBufferUserInput(TerminalBufferContent):
  def __init__(self, input: str) -> None:
    super().__init__()
    self._input = input

  def raw_content(self) -> str:
    """The unformatted buffer content."""
    return self._input

  def format(self) -> None:
    """Responsible for structuring the terminal message."""
    return f'{chr(0xE285)} {self._input}'

class TerminalBufferUnformattedText(TerminalBufferContent):
  def __init__(self, input: str) -> None:
    super().__init__()
    self._input = input

  def raw_content(self) -> str:
    """The unformatted buffer content."""
    return self._input
  
  def format(self) -> None:
    """Responsible for structuring the terminal message."""
    return self._input

class TerminalBufferErrorMessage(TerminalBufferContent):
  def __init__(self, input: str) -> None:
    super().__init__()
    self._input = input

  def raw_content(self) -> str:
    """The unformatted buffer content."""
    return self._input
  
  def format(self) -> None:
    """Responsible for structuring the terminal message."""
    return self._input

class TerminalBuffer():
  """Displays the previous commands and their output."""
  def __init__(self) -> None:
    self._scroll_back_buffer: Deque[TerminalBufferContent] = deque([], maxlen=SCROLL_BACK_BUFFER_MAX_LENGTH)
    self._history_buffer: Deque[TerminalBufferUserInput] = deque([], maxlen=HISTORY_BUFFER_MAX_LENGTH)
    self._active_prompt: str = ''
    self._cursor_location: int = 0

  def _remember(self, output: TerminalBufferUserInput) -> None:
    """Appends the provided output to the history buffer."""
    self._history_buffer.append(output)

  def add_text_to_prompt(self, char: str) -> None:
    """Adds text to the active prompt at the cursor location."""
    self._active_prompt = self._active_prompt[:self._cursor_location] + char + self._active_prompt[self._cursor_location:]
    self._cursor_location += len(char)

  def append_output(
    self, 
    output: TerminalBufferContent | List[TerminalBufferContent], 
    remember: bool = True
  ) -> None:
    """Add a line(s) to the scroll back buffer."""
    if isinstance(output, TerminalBufferContent):
      self._scroll_back_buffer.append(output)
      if remember:
        self._remember(output)
    elif isinstance(output, List):
      self._scroll_back_buffer.extend(output)

  def remove(self, num_chars_to_remove: int) -> None:
    """Remove N number of characters to the left of the active prompt."""
    # self._active_prompt = self._active_prompt[:-length]
    # self._cursor_location = max(0, self._cursor_location - length)

    self._active_prompt = self._active_prompt[0:self._cursor_location - num_chars_to_remove] + self._active_prompt[self._cursor_location:]
    self._cursor_location = max(0, self._cursor_location - num_chars_to_remove)
    

  def clear_prompt(self) -> None:
    """Empties the prompt."""
    self._active_prompt = ''
    self._cursor_location = 0

  def clear(self) -> None:
    """Empties the buffer and active prompt."""
    self._scroll_back_buffer.clear()
    self.clear_prompt()

  def shift_prompt_left(self, amount: int = 1) -> None:
    self._cursor_location = max(0, self._cursor_location - amount)

  def shift_prompt_right(self, amount: int = 1) -> None:
    self._cursor_location = min(len(self._active_prompt), self._cursor_location + 1)

  
  def history(self) -> List[str]:
    """Returns a copy of the history buffer."""
    return list(self._history_buffer)
  
  @property
  def active_prompt(self) -> str:
    return self._active_prompt

  @property
  def scroll_back_buffer(self) -> List[str]:
    return list(self._scroll_back_buffer)
  
  @property
  def cursor_location(self) -> int:
    return self._cursor_location