"""
A module that handles scanning the input of the console and converts it into 
a list of tokens.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, List


class TokenType(Enum):
  # Single character tokens.
  LEFT_PAREN  = auto() # (
  RIGHT_PAREN = auto() # )
  COMMA       = auto() # ,
  DOT         = auto() # .
  MINUS       = auto() # -
  PLUS        = auto() # +
  STAR        = auto() # *
  SLASH       = auto() # /
  BACKSLASH   = auto() # \

  # One or two character tokens.
  BANG          = auto() #!
  BANG_EQUAL    = auto() # !=
  EQUAL         = auto # =
  EQUAL_EQUAL   = auto # ==
  GREATER       = auto() # > 
  GREATER_EQUAL = auto () # >=
  LESS          = auto() # <
  LESS_EQUAL    = auto() # <=
  
  # Literals
  IDENTIFIER  = auto() 
  STRING      = auto() # could be via '...' or "..."
  NUMBER      = auto() # Integers and floating point
  
  # Internal
  EOF = auto() #End of the source string/file.

  # Keywords
    # TBD

@dataclass
class Token:
  type: TokenType
  lexeme: str
  literal: Any 
  line: int

"""
Commands
- clear
- ls (?)
- help <cmd>
- commands
"""


"""
What are the scanning use cases?
- Single Token Use cases
- Lexical errors
- Operators
- Division
- New lines, tabs, spaces
- String literals
- Number literals
- Reserved words
"""
class Lexer:
  def __init__(self) -> None:
    # All are set when scan is called.
    self._has_errors: bool
    self._start_pos: int 
    self._current_pos: int 
    self._current_line: int
    self._tokens: List[Token]
    self._source_code: str

  @property
  def errors_detected(self) -> bool:
    return self._has_errors

  def scan(self, input_code: str) -> List[Token]:
    self._source_code = input_code
    self._has_errors = False
    self._current_pos = 0
    self._current_line = 0
    self._tokens = []

    while self._current_pos <= len(self._source_code) - 1:
      self._start_pos = self._current_pos
      self._scan_token()

    self._tokens.append(Token(TokenType.EOF, '', None, self._current_line))
      
    return self._tokens

  def _log_error(self, line: int, msg: str) -> None:
    self._has_errors = True 
    print(f'Lexing Error: {msg}')

  def _scan_token(self) -> None:
    char: str = self._consume()
    self._step_forward()
    match char:
      case '(':
        self._add_token(TokenType.LEFT_PAREN)
      case ')':
        self._add_token(TokenType.RIGHT_PAREN)
      case ',':
        self._add_token(TokenType.COMMA)
      case '.':
        self._add_token(TokenType.DOT)
      case '-':
        self._add_token(TokenType.MINUS)
      case '+':
        self._add_token(TokenType.PLUS)
      case '*':
        self._add_token(TokenType.STAR)
      case '!':
        token_type = TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG
        self._add_token(token_type)
      case '=':
        token_type = TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL
        self._add_token(token_type)
      case '<':
        token_type = TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS
        self._add_token(token_type)
      case '>':
        token_type = TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER
        self._add_token(token_type)
      case ' ': # Skip spaces
        pass
      case _:
        self._log_error(self._current_line, f'Unexpected character: {char}')

  def _consume(self) -> str:
    return self._source_code[self._current_pos]

  def _step_forward(self) -> None:
    """Moves the scanner forward by one character."""
    self._current_pos = self._current_pos + 1

  def _add_token(self, type: TokenType, literal: Any = None) -> None:
    text = self._source_code[self._start_pos : self._current_pos]
    self._tokens.append(
      Token(
        type    = type, 
        lexeme  = text, 
        literal = literal, 
        line    = self._current_line
      )
    )

  def _match(self, expected: str) -> bool:
    if self._current_pos >= len(self._source_code):
      return False

    if self._source_code[self._current_pos] != expected:
      return False

    self._step_forward()
    return True