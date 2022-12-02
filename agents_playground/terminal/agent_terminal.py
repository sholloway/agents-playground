from __future__ import annotations
import traceback
from typing import List

import dearpygui.dearpygui as dpg

from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.tag import Tag
from agents_playground.terminal.ast import Expr, InlineASTFormatter, Stmt
from agents_playground.terminal.cmd_line_prompt import CommandLinePrompt
from agents_playground.terminal.interpreter import Interpreter, InterpreterRuntimeError
from agents_playground.terminal.lexer import Lexer, Token
from agents_playground.terminal.parser import ParseError, Parser
from agents_playground.terminal.terminal_action import TerminalAction
from agents_playground.terminal.terminal_buffer import TerminalBuffer, TerminalBufferErrorMessage, TerminalBufferUserInput
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
    
    # NOTE: A smart counter might be better here. 
    # But also may introduce dependency challenges.
    self._active_history_item: int = 0 

  def stdin(self, input: int) -> None:
    """Input stream for the terminal."""
    action, char = self._prompt.handle_prompt(input)
    match action:
      case TerminalAction.DO_NOTHING | None:
        pass
      case TerminalAction.CLOSE_TERMINAL:
        dpg.set_value(self._terminal_toggle_id, False)
      case TerminalAction.TYPE:
        self._terminal_buffer.append(char)
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.DELETE:
        self._terminal_buffer.remove(1)
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.DISPLAY_PREVIOUS:
        recent_history = self._terminal_buffer.history()
        history_length = len(recent_history)
        if history_length <= 0:
          return
        history_stmt: TerminalBufferUserInput = recent_history[history_length-1-self._active_history_item]
        self._terminal_buffer.clear_prompt()
        self._terminal_buffer.append(history_stmt.raw_content())
        self._active_history_item = min(history_length, self._active_history_item + 1)
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.DISPLAY_NEXT:
        recent_history: TerminalBufferUserInput = self._terminal_buffer.history()
        history_length = len(recent_history)
        if history_length <= 0:
          return
        history_stmt = recent_history[history_length-1-self._active_history_item]
        self._terminal_buffer.clear_prompt()
        self._terminal_buffer.append(history_stmt.raw_content())
        self._active_history_item = max(0, self._active_history_item - 1)
        self._display.refresh(self._terminal_buffer)
      case TerminalAction.RUN:
        # At this point pass the buffer to the Agent Shell...
        self._shell.run()

class AgentShell:
  def __init__(self, buffer: TerminalBuffer, display: TerminalDisplay) -> None:
    self._terminal_buffer = buffer
    self._terminal_display = display
    self._lexer = Lexer()
    self._interpreter = Interpreter(self._terminal_buffer, self._terminal_display)

  def run(self) -> None:
    try:
      tokens: List[Token] = self._lexer.scan(self._terminal_buffer.active_prompt)
      parser = Parser(tokens)
      statements: List[Stmt] = parser.parse()
      self._terminal_buffer.append_output(TerminalBufferUserInput(self._terminal_buffer.active_prompt))

      if parser._encountered_error:
        self._terminal_buffer.append_output(TerminalBufferErrorMessage('Encountered a parser error.'))
      elif statements is None:
        self._terminal_buffer.append_output(TerminalBufferErrorMessage('Parser returned NoneType.'))
      else:
        # # Print the AST
        # formatted_ast = InlineASTFormatter().format(expr)
        # buffer.append_output(f'{chr(0xE285)} {formatted_ast}')
        
        # Attempt to evaluate the expression.
        self._interpreter.interpret(statements)
        # buffer.append_output(f'{chr(0xE285)} {str(expr_result)}')

      self._terminal_buffer.clear_prompt()
      self._terminal_display.refresh(self._terminal_buffer)
    except ParseError as pe:
      generic_error_msg = 'An error was detected while parsing.'
      specific_info     = f'Line: {pe.token.line} {pe.token.type}'
      error_msg         = pe.args[0]
      self._terminal_buffer.append_output(TerminalBufferErrorMessage(f'{generic_error_msg}'), remember=False)
      self._terminal_buffer.append_output(TerminalBufferErrorMessage(f'{specific_info}'), remember=False)
      self._terminal_buffer.append_output(TerminalBufferErrorMessage(f'{error_msg}'), remember=False)
      self._terminal_display.refresh(self._terminal_buffer)
    except InterpreterRuntimeError as re:
      generic_error_msg = 'An error was detected while interpreting.'
      specific_info     = f'Line: {re.token.line} {re.token.type}'
      error_msg         = re.args[0]
      self._terminal_buffer.append_output(TerminalBufferErrorMessage(f'{generic_error_msg}'), remember=False)
      self._terminal_buffer.append_output(TerminalBufferErrorMessage(f'{specific_info}'), remember=False)
      self._terminal_buffer.append_output(TerminalBufferErrorMessage(f'{error_msg}'), remember=False)
      self._terminal_display.refresh(self._terminal_buffer)
    except BaseException as be:
      # TODO: Incorporate logging.
      print('An exception was thrown attempting to process the terminal input.')
      traceback.print_exception(be)

  