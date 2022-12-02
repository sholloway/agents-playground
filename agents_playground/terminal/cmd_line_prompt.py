from typing import Tuple
from agents_playground.terminal.key_interpreter import KeyCode, KeyInterpreter
from agents_playground.terminal.terminal_action import TerminalAction

Prompt = str
class CommandLinePrompt:
  """Responsible for receiving input from the user and representing what they type."""
  def __init__(self) -> None:
    self._key_interpreter = KeyInterpreter()

  def handle_prompt(self, code: KeyCode) -> Tuple[TerminalAction, Prompt | None]:
    char = self._key_interpreter.key_to_char(code)
    result: Tuple[TerminalAction, Prompt]
    
    match char:
      case None:
        result = (TerminalAction.DO_NOTHING, None)
      case 'ESC': # Close the terminal
        result = (TerminalAction.CLOSE_TERMINAL, char)
      case '\b': # Delete a character
        result = (TerminalAction.DELETE, char)
      case '\n':
        result = (TerminalAction.RUN, char)
      case 'DOWN_ARROW':
        result = (TerminalAction.DISPLAY_NEXT, None)
      case 'UP_ARROW':
        result = (TerminalAction.DISPLAY_PREVIOUS, None)
      case 'LEFT_ARROW':
        result = (TerminalAction.MOVE_PROMPT_LEFT, None)
      case 'RIGHT_ARROW':
        result = (TerminalAction.MOVE_PROMPT_RIGHT, None)
      case _: # Type a character
        result = (TerminalAction.TYPE, char)
    return result