"""
A module that handles scanning the input of the console and converts it into 
a list of tokens.
"""
from __future__ import annotations

from typing import Any, List
import string
from agents_playground.terminal.token import Token

from agents_playground.terminal.token_type import TokenType

RESERVED_WORDS_MAP: dict[str, TokenType] = {
  'var'     : TokenType.VAR,
  'if'      : TokenType.IF,
  'else'    : TokenType.ELSE,
  'and'     : TokenType.AND,
  'or'      : TokenType.OR,
  'True'    : TokenType.TRUE,
  'False'   : TokenType.FALSE,
  'clear'   : TokenType.CLEAR,
  'print'   : TokenType.PRINT,
  'history' : TokenType.HISTORY
}

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
      case '{':
        self._add_token(TokenType.LEFT_BRACE)
      case '}':
        self._add_token(TokenType.RIGHT_BRACE)
      case ';':
        self._add_token(TokenType.SEMICOLON)
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
      case '/':
        self._add_token(TokenType.SLASH)
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
      case ' ' | '\r' | '\t': # Skip spaces
        pass
      case '\n': # Handle new lines
        self._current_line = self._current_line + 1
      case '"':
        self._handle_fat_string_literal()
      case '\'':
        self._handle_skinny_string_literal()
      case _ if self._is_digit(char):
        self._handle_number_literal()
      case _ if self._is_alpha(char):
        self._handle_identifier()
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
    if self._at_end():
      return False

    if self._source_code[self._current_pos] != expected:
      return False

    self._step_forward()
    return True

  def _at_end(self) -> bool:
    return self._current_pos >= len(self._source_code)

  def _peek(self, additional_steps=0) -> str:
    """Look ahead without moving the current position."""
    if (self._current_pos + additional_steps) >= len(self._source_code):
      return '\0'
    else:
      return self._source_code[self._current_pos + additional_steps]

  def _handle_fat_string_literal(self) -> None:
    while self._peek() != '"' and not self._at_end():
      if self._peek() == '\n':
        self._current_line = self._current_line + 1
      self._step_forward()

    if self._at_end():
      self._log_error(self._current_line, 'Unterminated string.')

    self._step_forward() # Grab the closing '"'

    scan_start = self._start_pos + 1
    scan_stop = self._current_pos - 1
    string_literal = self._source_code[scan_start : scan_stop]
    self._add_token(TokenType.STRING, string_literal)
  
  def _handle_skinny_string_literal(self) -> None:
    while self._peek() != '\'' and not self._at_end():
      if self._peek() == '\n':
        self._current_line = self._current_line + 1
      self._step_forward()

    if self._at_end():
      self._log_error(self._current_line, 'Unterminated string.')

    self._step_forward() # Grab the closing '\''

    scan_start = self._start_pos + 1
    scan_stop = self._current_pos - 1
    string_literal = self._source_code[scan_start : scan_stop]
    self._add_token(TokenType.STRING, string_literal)

  def _is_digit(self, char) -> bool:
    return char in string.digits

  def _is_alpha(self, char) -> bool:
    return char in string.ascii_letters or \
      char == '_'

  def _is_alpha_numeric(self, char) -> bool:
    return self._is_alpha(char) or self._is_digit(char)

  def _handle_number_literal(self) -> None:
    is_complex_number: bool = False
    while self._is_digit(self._peek()):
      self._step_forward()

    # Handle right of the decimal place for fractional numbers.
    if self._peek() == '.' and self._is_digit(self._peek(additional_steps = 1)):
      is_complex_number = True

      # Consume the "."
      self._step_forward()

      # consume the numbers to the right of the decimal place.
      while self._is_digit(self._peek()):
        self._step_forward()

    value = self._source_code[self._start_pos : self._current_pos]
    token_value: int | float = float(value) if is_complex_number else int(value)
    self._add_token(TokenType.NUMBER, token_value)

  def _handle_identifier(self) -> None:
    while self._is_alpha_numeric(self._peek()):
      self._step_forward()

    text = self._source_code[self._start_pos : self._current_pos]

    token_type: TokenType | None = RESERVED_WORDS_MAP.get(text)

    # If the last token type was TokenType.Var and this is None, then 
    # the token type should be TokenType.IDENTIFIER
    
    match token_type:
      case TokenType.TRUE:
        self._add_token(token_type, literal = True)
      case TokenType.FALSE:
        self._add_token(token_type, literal = False)
      case None:
        self._add_token(TokenType.IDENTIFIER)
      case _:
        self._add_token(token_type)