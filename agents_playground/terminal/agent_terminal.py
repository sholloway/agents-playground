from __future__ import annotations
from typing import List

import dearpygui.dearpygui as dpg

from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.tag import Tag
from agents_playground.terminal.agent_shell import AgentShell
from agents_playground.terminal.agent_terminal_state import AgentTerminalMode
from agents_playground.terminal.cmd_line_prompt import CommandLinePrompt
from agents_playground.terminal.terminal_action import TerminalAction
from agents_playground.terminal.terminal_buffer import TerminalBuffer, TerminalBufferContent
from agents_playground.terminal.terminal_display import TerminalDisplay

"""
Some Terms:
- Terminal: A terminal is a text input and output environment.
- Console: A physical terminal is referred to as a console.
- Shell: The shell is a command-line interpreter.
- Command-line: A command line, also known as a command prompt, is a type of interface.
- REPL: Read-Eval-Print Loop
  Lisp REPL example:  (print (eval env (read)))

From a design perspective I think I want
Simulation  
  ->  AgentTerminal  
      ->  stdin/ stdout/ stderr?
      ->  CommandLine Prompt  
            ->  KeyInterpreter
      ->  Output Buffer
      ->  Shell 
          -> OS Hooks
          ->  REPL  -> Lexer
                    -> Parser
                    -> Transpiler
                    -> VM... Python exec... etc...

I'd like to have some programmer sugar. 
- Display !=, >=, infinity, etc.
- Color code errors.
- Table output for queries
- Draw AST trees
- Copy/Paste

To do some of that I need to have another layer of abstraction between 
what is typed, what is displayed, and what is processed by the Lexer.
- The KeyInterpreter should probably get smarter. A thought is to run 
  the command line through the lexer and parser on every key stroke and then 
  apply a syntax highlighter visitor to the AST. 
- This approach would enable doing suggestions using a Splay or Trie tree data structure.

Considerations:
- Color the > prompt. Green for just starting or last cmd successful. Red for last command failed.

- Figure out the background scaling issue on the console.
- Up/Down Arrow cycles through previous cmds.
- <Enter> runs a line unless there is a \ at the end of the line. Then it adds a \n.
- The <clear> command deletes the buffer and resets the line to 0.
- I need the concept of a scrollback buffer. Everything added to the console 
  is appended to the buffer and displayed. 
  A secondary thing <name> is used to represent where the user is typing.
- Set the width for text wrapping.
- Key Concepts in Terminals
  - Scrollback Buffer
  - TTY
  - termcap


  TODO: 
  Use Case: Support auto indent.
  - Auto indent on the braces ({}).

  Behavior
  - When a user opens { increment the indent count.
  - When a user closes }, decrement the indent count.
  - When a new line is created (in the same active prompt),
    start the prompt at the number of tabs the indent count is at.
  - Reset the indent count when the active prompt is run.

  The naive implementation is to just use a counter to track when the 
  user types '{' or '}'. It would be more powerful to lex and parser the code 
  on every key stroke. Then have a secondary interpreter that takes action
  such has auto indent. 

  Really, I should implement a proper syntax highlighter and have this functionality
  build on top of that.

  Use Case: Evaluate 1 line expressions.
"""                   

class AgentTerminal:
  def __init__(self, 
    terminal_layer_id: Tag, 
    display_id: Tag, 
    terminal_toggle_id: Tag, 
    context: SimulationContext) -> None:
    self._terminal_toggle_id = terminal_toggle_id
    self._display = TerminalDisplay(terminal_layer_id, display_id, context)
    self._prompt = CommandLinePrompt()
    self._terminal_buffer = TerminalBuffer()
    self._shell = AgentShell(self._terminal_buffer, self._display)
    self._active_history_item: int = 0 
    self._terminal_mode = AgentTerminalMode.COMMAND

  def stdin(self, input: int) -> None:
    """Input stream for the terminal."""
    recent_history: List[TerminalBufferContent]
    action, char = self._prompt.handle_prompt(input, self._terminal_mode)
    match action:
      case TerminalAction.DO_NOTHING:
        pass
      case TerminalAction.CLOSE_TERMINAL:
        dpg.set_value(self._terminal_toggle_id, False)
      case TerminalAction.TYPE:
        self._terminal_buffer.add_text_to_active_line(char)
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.DELETE:
        self._terminal_buffer.remove(1)
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.NEW_LINE:
        self._terminal_mode = AgentTerminalMode.INSERT
        self._terminal_buffer.add_new_line()
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.DISPLAY_PREVIOUS:
        recent_history = self._terminal_buffer.history()
        history_length = len(recent_history)
        if history_length <= 0:
          return
        history_stmt: TerminalBufferContent = recent_history[history_length-1-self._active_history_item]
        self._terminal_buffer.clear_prompt()
        self._terminal_buffer.add_text_to_active_line(history_stmt.raw_content())
        self._active_history_item = min(history_length, self._active_history_item + 1)
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.DISPLAY_NEXT:
        recent_history = self._terminal_buffer.history()
        history_length = len(recent_history)
        if history_length <= 0:
          return
        history_stmt = recent_history[history_length-1-self._active_history_item]
        self._terminal_buffer.clear_prompt()
        self._terminal_buffer.add_text_to_active_line(history_stmt.raw_content())
        self._active_history_item = max(0, self._active_history_item - 1)
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.MOVE_PROMPT_LEFT:
        self._terminal_buffer.shift_prompt_left()
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.MOVE_PROMPT_RIGHT:
        self._terminal_buffer.shift_prompt_right()
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.MOVE_PROMPT_DOWN:
        self._terminal_buffer.shift_prompt_down()
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.MOVE_PROMPT_UP:
        self._terminal_buffer.shift_prompt_up()
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.RUN:
        self._shell.run(self._terminal_mode)
        self._terminal_mode = AgentTerminalMode.COMMAND