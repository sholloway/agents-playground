"""
A recursive descent parser for the Agent Terminal language.
"""

from typing import List
from agents_playground.terminal.ast import BinaryExpr, Clear, Expr, GroupingExpr, LiteralExpr, Print, Stmt, UnaryExpr
from agents_playground.terminal.token import Token
from agents_playground.terminal.token_type import TokenType

"""
Each statement in the grammar maps to a function on the parser.
The grammar...
program     -> statement* EOF ;
statement   -> exprStmt | printStmt | clearStmt;
exprStmt    -> expression ";" ;
printStmt   -> "print" expression ";" ;
clearStmt   -> "clear" ";" ;  # SDH - I'm adding this to clear the REPL screen.

expression  -> equality;
equality    -> comparison ( ( "!=" | "==" ) comparison )*;
comparison  -> term ( (">" | ">=" | "<" | "<=") term )*;
term        -> factor ( ( "-" | "+") factor )*;
factor      -> unary ( ( "/" | "*") unary )*;
unary       -> ( "!" | "-" ) unary | primary ;
primary     -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")";
"""

class ParseError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class Parser:
  def __init__(self, tokens: List[Token]) -> None:
    self._tokens = tokens
    self._current = 0
    self._encountered_error = False

  def parse(self) -> List[Stmt]:
    statements: List[Stmt] = []
    while not self._is_at_end():
      statements.append(self._statement())
    return statements

  """
  Implements Grammar Rule
  expression -> equality;
  """
  def _expression(self) -> Expr:
    return self._equality()


  """
  Implements Grammar Rule
  statement -> exprStmt | printStmt | clearStmt;
  """
  def _statement(self) -> Stmt:
    if self._match(TokenType.PRINT):
      return self._print_statement()
    
    if self._match(TokenType.CLEAR):
      return self._clear_statement()
    return self._expression_stmt()


  def _print_statement(self) -> Stmt:
    value: Expr = self._expression()
    self._consume(TokenType.SEMICOLON, "Expect a ';' after value.")
    return Print(value)
  
  def _clear_statement(self) -> Stmt:
    self._consume(TokenType.SEMICOLON, "Expect a ';' after value.")
    return Clear()

  """
  Implements Grammar Rule
  equality -> comparison ( ( "!=" | "==" ) comparison )*;
  """
  def _equality(self) -> Expr:
    expr: Expr = self._comparison()
    while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
      operator: Token = self._previous()
      right: Expr = self._comparison()
      expr = BinaryExpr(expr, operator, right)
    return expr

  def _match(self, *types: TokenType) -> bool:
    for type in types:
      if self._check(type):
        self._advance()
        return True
    return False

  def _check(self, type: TokenType) -> bool:
    if self._is_at_end():
      return False
    return self._peek().type == type

  def _advance(self) -> None:
    if not self._is_at_end():
      self._current += 1
    return self._previous()

  def _is_at_end(self):
    return self._peek().type == TokenType.EOF

  def _peek(self) -> Token:
    return self._tokens[self._current]

  def _previous(self) -> Token:
    return self._tokens[self._current - 1]

  """
  Implements Grammar Rule
  comparison -> term ( (">" | ">=" | "<" | "<=") term )*;
  """
  def _comparison(self) -> Expr:
    expr: Expr = self._term()
    while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
      operator: Token = self._previous()
      right: Expr = self._term()
      expr = BinaryExpr(expr, operator, right)
    return expr

  """
  Implements Grammar Rule
  term -> factor ( ( "-" | "+") unary )*;
  """
  def _term(self) -> Expr:
    expr: Expr = self._factor()
    while self._match(TokenType.MINUS, TokenType.PLUS):
      operator: Token = self._previous()
      right: Expr = self._factor()
      expr = BinaryExpr(expr, operator, right)
    return expr

  """
  Implements Grammar Rule
  factor -> unary ( ( "/" | "*") unary )*;
  """
  def _factor(self) -> Expr:
    expr: Expr = self._unary()
    while self._match(TokenType.SLASH, TokenType.STAR):
      operator: Token = self._previous()
      right: Expr = self._unary()
      expr = BinaryExpr(expr, operator, right)
    return expr

  """
  Implements Grammar Rule
  unary -> ( "!" | "-" ) unary | primary ;
  """
  def _unary(self) -> Expr:
    if self._match(TokenType.BANG, TokenType.MINUS):
      operator: Token = self._previous()
      right: Expr = self._unary()
      return UnaryExpr(operator, right)
    return self._primary()

  """
  Implements Grammar Rule
  primary -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")";
  """
  def _primary(self) -> Expr:
    if self._match(TokenType.FALSE):
      return LiteralExpr(False)
    elif self._match(TokenType.TRUE): #I'm expecting to hit here.
      return LiteralExpr(True)
    elif self._match(TokenType.NONE):
      return LiteralExpr(None)
    elif self._match(TokenType.NUMBER, TokenType.STRING):
      return LiteralExpr(self._previous().literal)
    elif self._match(TokenType.LEFT_PAREN):
      expr: Expr = self._expression()
      self._consume(TokenType.RIGHT_PAREN, f'Expect ) after expression.')
      return GroupingExpr(expr)

  def _consume(self, type: TokenType, error_msg: str) -> Token:
    if self._check(type):
      return self._advance()
    else:
      raise self._error(self._peek(), error_msg)

  def _error(self, token: Token, error_msg: str) -> ParseError:
    self._handle_error(token, error_msg)
    return ParseError()

  def _handle_error(self, token: Token, error_msg: str) -> None:
    if token.type == TokenType.EOF:
      self._report(token.line, "At end", error_msg)
    else:
      self._report(token.line, f'At \'{token.lexeme}\'', error_msg)

  # Bug: Don't write with print here. I need to route this back to the Terminal.
  def _report(line: int, *messages: str) -> None:
    print(f'Error on line {line}')
    for msg in messages:
      print(msg)
