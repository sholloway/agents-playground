from __future__ import annotations
from collections import deque
from typing import Deque, List, Tuple

import dearpygui.dearpygui as dpg

from enum import Enum, auto
from agents_playground.core.constants import DEFAULT_FONT_SIZE
from agents_playground.renderers.color import Colors
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.tag import Tag
from agents_playground.terminal.ast import Expr, InlineASTFormatter
from agents_playground.terminal.interpreter import Interpreter
from agents_playground.terminal.key_interpreter import KeyCode, KeyInterpreter
from agents_playground.terminal.lexer import Lexer, Token
from agents_playground.terminal.parser import Parser

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

class TerminalAction(Enum):
  DO_NOTHING      = auto()
  CLOSE_TERMINAL  = auto()
  TYPE            = auto()
  DELETE          = auto()
  RUN             = auto()
  
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
    self._shell = AgentShell()


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
      case TerminalAction.RUN:
        # At this point pass the buffer to the Lexer...
        self._shell.run(self._terminal_buffer, self._display)

TERM_DISPLAY_INITIAL_TOP_OFFSET = 10
TERM_DISPLAY_LEFT_OFFSET = 10
TERM_DISPLAY_LINE_HEIGHT = DEFAULT_FONT_SIZE
TERM_DISPLAY_VERTICAL_LINE_SPACE = 4
TERM_DISPLAY_HORIZONTAL_LINE_SPACE = 10

class TerminalDisplay:
  def __init__(
    self, 
    terminal_layer_id: Tag, 
    display_id: Tag, 
    context: SimulationContext
  ) -> None:
    self._terminal_layer_id = terminal_layer_id
    self._display_id        = display_id
    self._context           = context

  def refresh(self, screen_buffer: TerminalBuffer) -> None:
    """
    Because I want to use a rolling screen buffer for the output and I want to 
    colorize text, I can't use a single draw_text command that I update.
    I need a way to add draw_text commands in a loop.

    On container's Slot 2 is used for draw items.
    I think a refresh could ideally be to:
    1. Clear Slot 2 on the terminal draw_layer.
    2. Add loop through the deque scroll_back_buffer and add a draw_text for each
       item. I can add to a layer by setting the layer as the parent on the draw_text.
    3. Draw the active command prompt. There is probably an optimization I could 
       do to not do steps 1 - 2 when typing.   
    """
    # Clear all drawable Items
    dpg.delete_item(
      item = self._terminal_layer_id, 
      children_only=True, 
      slot = 2
    )

    # Draw the background
    dpg.draw_rectangle(
      parent = self._terminal_layer_id,
      pmin = (0, 0),
      pmax = (self._context.canvas.width, self._context.canvas.height),
      fill = (30, 30, 30)
    )

    # Draw the Output Buffer if any.
    current_line: int = 0
    vertical_offset: int = 0
    for line in screen_buffer.scroll_back_buffer:
      vertical_offset = TERM_DISPLAY_INITIAL_TOP_OFFSET + \
        (current_line * TERM_DISPLAY_LINE_HEIGHT) + \
        (current_line * TERM_DISPLAY_VERTICAL_LINE_SPACE)
      current_line = current_line + 1

      dpg.draw_text(
        parent = self._terminal_layer_id,
        pos   = (TERM_DISPLAY_LEFT_OFFSET, vertical_offset),
        text  = line, 
        color = (204, 204, 204),
        size  = DEFAULT_FONT_SIZE
      )

    # Draw the Command Prompt.
    cmd_prompt = f'{screen_buffer.active_prompt}{chr(0x2588)}'
    vertical_offset = TERM_DISPLAY_INITIAL_TOP_OFFSET + \
        (current_line * TERM_DISPLAY_LINE_HEIGHT) + \
        (current_line * TERM_DISPLAY_VERTICAL_LINE_SPACE)
    dpg.draw_text(
      parent = self._terminal_layer_id,
      pos   = (TERM_DISPLAY_LEFT_OFFSET, vertical_offset),
      text  = chr(0xE285), 
      color = Colors.green.value,
      size  = DEFAULT_FONT_SIZE
    )
    dpg.draw_text(
        parent = self._terminal_layer_id,
        pos   = (TERM_DISPLAY_LEFT_OFFSET + DEFAULT_FONT_SIZE, vertical_offset),
        text  = cmd_prompt, 
        color = (204, 204, 204),
        size  = DEFAULT_FONT_SIZE
      )

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
      case _: # Type a character
        result = (TerminalAction.TYPE, char)
    return result
          

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

class AgentShell:
  def __init__(self) -> None:
    self._lexer = Lexer()
    self._interpreter = Interpreter()

  def run(self, buffer: TerminalBuffer, display: TerminalDisplay) -> None:
    tokens: List[Token] = self._lexer.scan(buffer.active_prompt)
    parser = Parser(tokens)
    expr: Expr = parser.parse()
    buffer.append_output(f'{chr(0xE285)} {buffer.active_prompt}')

    if parser._encountered_error:
      buffer.append_output(f'{chr(0xE285)} Encountered a parser error.')
    elif expr is None:
      buffer.append_output(f'{chr(0xE285)} Parser returned NoneType.')
    else:
      # Print the AST
      formatted_ast = InlineASTFormatter().format(expr)
      buffer.append_output(f'{chr(0xE285)} {formatted_ast}')
      
      # Attempt to evaluate the expression.
      expr_result = self._interpreter.interpret(expr)
      buffer.append_output(f'{chr(0xE285)} {str(expr_result)}')

    buffer.clear_prompt()
    display.refresh(buffer)