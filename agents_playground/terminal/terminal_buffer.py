from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, List

from agents_playground.counter.counter import Counter

SCROLL_BACK_BUFFER_MAX_LENGTH = 30
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
    self._history_buffer: Deque[TerminalBufferUserInput]   = deque([], maxlen=HISTORY_BUFFER_MAX_LENGTH)
    """
    The active prompt is the text the user is actively working with. To support
    multiple lines, a list of strings is use. In which each item in the list 
    represents a line of text in the terminal.
    """
    self._active_prompt: List[str] = [''] 
    self._cursor_horizontal_position = Counter(start = 0, min_value = 0, increment_step=1,decrement_step=1)
    self._cursor_vertical_position = Counter(start = 0, min_value = 0, increment_step=1,decrement_step=1)
    
  def _remember(self, output: TerminalBufferUserInput | List[TerminalBufferUserInput]) -> None:
    """Appends the provided output to the history buffer."""
    if isinstance(output, TerminalBufferUserInput):
      self._history_buffer.append(output)
    elif isinstance(output, List):
      self._history_buffer.extend(output)

  def add_new_line(self) -> None:
    """Adds a new line to the active prompt."""
    self._active_prompt.append('')
    self._cursor_vertical_position.increment()
    self._cursor_horizontal_position.reset()

  def add_text_to_active_line(self, char: str) -> None:
    """Adds text to the active prompt at the cursor location."""
    prompt_line = self._cursor_vertical_position.value()
    cursor_loc = self._cursor_horizontal_position.value()
    
    self._active_prompt[prompt_line] = \
      self._active_prompt[prompt_line][:cursor_loc] + \
      char + \
      self._active_prompt[prompt_line][cursor_loc:]

    for _ in range(len(char)):
      self._cursor_horizontal_position.increment()

  def append_output(
    self, 
    output: TerminalBufferContent | List[TerminalBufferContent], 
    remember: bool = True
  ) -> None:
    """Add a line(s) to the scroll back buffer."""
    if isinstance(output, TerminalBufferContent):
      self._scroll_back_buffer.append(output)
    elif isinstance(output, List):
      self._scroll_back_buffer.extend(output)
    if remember:
      self._remember(output)

  def remove(self, num_chars_to_remove: int) -> None:
    """Remove N number of characters to the left of the active prompt."""
    prompt_line = self._cursor_vertical_position.value()
    cursor_loc = self._cursor_horizontal_position.value()
    
    self._active_prompt[prompt_line] = \
      self._active_prompt[prompt_line][0:cursor_loc - num_chars_to_remove] + \
      self._active_prompt[prompt_line][cursor_loc:]

    for _ in range(num_chars_to_remove):
      self._cursor_horizontal_position.decrement()
    
  def clear_prompt(self) -> None:
    """Empties the prompt."""
    self._active_prompt = ['']
    self._cursor_horizontal_position.reset()

  def clear(self) -> None:
    """Empties the buffer and active prompt."""
    self._scroll_back_buffer.clear()
    self.clear_prompt()

  def shift_prompt_left(self, amount: int = 1) -> None:
    """Move the input prompt to the left."""
    for _ in range(amount):
      self._cursor_horizontal_position.decrement()

  def shift_prompt_right(self, amount: int = 1) -> None:
    """Move the input prompt to the right."""
    prompt_line = len(self._active_prompt) - 1
    for _ in range(amount):
      if self._cursor_horizontal_position.value() < len(self._active_prompt[prompt_line]):
        self._cursor_horizontal_position.increment()

  def shift_prompt_down(self, amount: int = 1) -> None:
    """Move the input prompt down."""
    num_lines = self.prompt_lines()
    for _ in range(amount):
      if self._cursor_vertical_position.value() < num_lines - 1:
        self._cursor_vertical_position.increment()
  
  def shift_prompt_up(self, amount: int = 1) -> None:
    """Move the input prompt up."""
    for _ in range(amount):
      self._cursor_vertical_position.decrement()
  
  def history(self) -> List[str]:
    """Returns a copy of the history buffer."""
    return list(self._history_buffer)
  
  def prompt_lines(self) -> int:
    """Returns the number of lines in the active prompt."""
    return len(self._active_prompt)

  @property
  def active_prompt(self) -> List[str]:
    return self._active_prompt

  @property
  def scroll_back_buffer(self) -> List[str]:
    return list(self._scroll_back_buffer)
  
  @property
  def cursor_horizontal_location(self) -> int:
    return self._cursor_horizontal_position.value()
  
  @property
  def cursor_vertical_location(self) -> int:
    return self._cursor_vertical_position.value()