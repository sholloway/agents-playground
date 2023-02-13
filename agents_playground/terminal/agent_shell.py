import traceback
from typing import List

from agents_playground.terminal.agent_terminal_state import AgentTerminalMode
from agents_playground.terminal.ast.statements import Stmt
from agents_playground.terminal.constants import TERMINAL_TO_INTERPRETER_MODE
from agents_playground.terminal.lexer import Lexer, Token
from agents_playground.terminal.parser import ParseError, Parser
from agents_playground.terminal.resolver import Resolver
from agents_playground.terminal.terminal_display import TerminalDisplay
from agents_playground.terminal.terminal_buffer import (
  TerminalBuffer, 
  TerminalBufferContent, 
  TerminalBufferErrorMessage, 
  TerminalBufferUserInput
)
from agents_playground.terminal.terminal_interpreter import (
  TerminalInterpreter, 
  InterpreterMode, 
  InterpreterRuntimeError
)

class AgentShell:
  def __init__(self, buffer: TerminalBuffer, display: TerminalDisplay) -> None:
    self._terminal_buffer = buffer
    self._terminal_display = display
    self._lexer = Lexer()
    self._interpreter = TerminalInterpreter(self._terminal_buffer, self._terminal_display)
    self._resolver = Resolver(self._interpreter)

  def handle_parser_errors(self, line_num: int, messages: List[str]) -> None:
    generic_error_msg = 'Syntax Error'
    self._terminal_buffer.append_output(TerminalBufferErrorMessage(generic_error_msg), remember=False)
    self._terminal_buffer.append_output(TerminalBufferErrorMessage(f'Error on line {line_num}'), remember=False)
    for msg in messages:
      self._terminal_buffer.append_output(TerminalBufferErrorMessage(msg), remember=False)
    self._terminal_display.refresh(self._terminal_buffer)

  def run(self, terminal_mode: AgentTerminalMode) -> None:
    try:
      # 1. Lex the code. 
      code: str = '\n'.join(self._terminal_buffer.active_prompt)
      tokens: List[Token] = self._lexer.scan(code)

      # 2. Build an AST from the stream of tokens. 
      parser = Parser(tokens, error_handler=self.handle_parser_errors)
      statements: List[Stmt] = parser.parse()
      history: List[TerminalBufferContent] = list(map(lambda line: TerminalBufferUserInput(line), self._terminal_buffer.active_prompt))
      self._terminal_buffer.append_output(history)

      if parser._encountered_error:
        self._terminal_buffer.append_output(TerminalBufferErrorMessage('Encountered a parser error.'))
      elif statements is None:
        self._terminal_buffer.append_output(TerminalBufferErrorMessage('Parser returned NoneType.'))
      else:
        # 3. Perform lexical scope analysis to determine variable scoping and binding.
        self._resolver.resolve(statements)
        if self._resolver.encounter_errors():
          print("The resolver encountered errors")
          for error in self._resolver._errors:
            print(f'{error[0]}: {error[1]}')
          return

        #4. Attempt to run the code.
        interpreter_mode: InterpreterMode = TERMINAL_TO_INTERPRETER_MODE[terminal_mode]
        self._interpreter.interpret(statements, interpreter_mode)

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