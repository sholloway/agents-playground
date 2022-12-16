from typing import Tuple
from agents_playground.terminal.agent_terminal_state import AgentTerminalMode
from agents_playground.terminal.keyboard.key_interpreter import KeyCode, KeyInterpreter
from agents_playground.terminal.terminal_action import TerminalAction

Prompt = str
class CommandLinePrompt:
  """Responsible for receiving input from the user and representing what they type."""
  def __init__(self) -> None:
    self._key_interpreter = KeyInterpreter()

  def handle_prompt(self, code: KeyCode, terminal_mode: AgentTerminalMode) -> Tuple[TerminalAction, Prompt]:
    char = self._key_interpreter.key_to_char(code)
    result: Tuple[TerminalAction, Prompt]
    
    match char:
      case None:
        result = (TerminalAction.DO_NOTHING, '')
      case 'ESC': # Close the terminal
        result = (TerminalAction.CLOSE_TERMINAL, char)
      case '\b': # Delete a character
        result = (TerminalAction.DELETE, char)
      case 'RUN_CODE':
        result = (TerminalAction.RUN, char)
      case 'NEW_LINE':
        result = (TerminalAction.NEW_LINE, char)
      case 'DOWN_ARROW' if terminal_mode == AgentTerminalMode.COMMAND:
        result = (TerminalAction.DISPLAY_NEXT, '')
      case 'UP_ARROW' if terminal_mode == AgentTerminalMode.COMMAND:
        result = (TerminalAction.DISPLAY_PREVIOUS, '')
      case 'DOWN_ARROW' if terminal_mode == AgentTerminalMode.INSERT:
        result = (TerminalAction.MOVE_PROMPT_DOWN, '')
      case 'UP_ARROW' if terminal_mode == AgentTerminalMode.INSERT:
        result = (TerminalAction.MOVE_PROMPT_UP, '')
      case 'LEFT_ARROW':
        result = (TerminalAction.MOVE_PROMPT_LEFT, '')
      case 'RIGHT_ARROW':
        result = (TerminalAction.MOVE_PROMPT_RIGHT, '')
      case _: # Type a character
        result = (TerminalAction.TYPE, char)
    return result