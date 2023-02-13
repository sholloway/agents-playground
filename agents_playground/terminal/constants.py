# The maximum number of arguments allowed in a function call.
from typing import Dict
from agents_playground.terminal.agent_terminal_state import AgentTerminalMode
from agents_playground.terminal.terminal_interpreter import InterpreterMode


TERM_MAX_ARG_SIZE = 255

TERMINAL_TO_INTERPRETER_MODE: Dict[AgentTerminalMode, InterpreterMode] = {
  AgentTerminalMode.COMMAND: InterpreterMode.COMMAND,
  AgentTerminalMode.INSERT: InterpreterMode.INSERT
}