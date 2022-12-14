"""
A recursive descent parser for the Agent Terminal language.
"""

from typing import List
from agents_playground.terminal.ast.statements import ( 
  Block,
  Expression,
  If,
  Stmt, 
  Clear, 
  History, 
  Print,
  Var 
)
from agents_playground.terminal.ast.expressions import ( 
  Assign,
  Expr,
  BinaryExpr, 
  GroupingExpr, 
  LiteralExpr,
  LogicalExpr, 
  UnaryExpr,
  Variable
)
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
  def __init__(self, token: Token, error_msg:str) -> None:
    super().__init__(error_msg)
    self._token = token

  @property
  def token(self) -> Token:
    return self._token

class Parser:
  def __init__(self, tokens: List[Token]) -> None:
    self._tokens = tokens
    self._current = 0
    self._encountered_error = False

  def parse(self) -> List[Stmt]:
    statements: List[Stmt] = []
    while not self._is_at_end():
      statements.append(self._declaration())
    return statements


  def _declaration(self) -> Stmt:
    try:
      if self._match(TokenType.VAR):
        return self._var_declaration()
      else:
        return self._statement()
    except ParseError as pe:
      self._synchronize()
      # TODO: Handle synchronization...

  def _synchronize(self) -> None:
    """When an error has occurred parsing, jump forward until the next viable token is discovered."""
    self._advance()
    while not self._is_at_end():
      if self._previous() == TokenType.SEMICOLON:
        return;

    next_token: Token = self._peek()
  
    match next_token.type:
      case TokenType.VAR | TokenType.PRINT | TokenType.CLEAR | TokenType.HISTORY:
        return
    
    self._advance()

  def _var_declaration(self) -> Stmt:
    name: Token = self._consume(TokenType.IDENTIFIER, 'Expected variable name.')
    initializer: Expr;
    if self._match(TokenType.EQUAL):
      initializer = self._expression()
    
    self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
    return Var(name, initializer)
    
  """
  Implements Grammar Rule
  expression -> assignment;
  """
  def _expression(self) -> Expr:
    return self._assignment()

  """
  Implements Grammar Rule
  assignment  -> IDENTIFIER "=" assignment | logic_or ;
  """
  def _assignment(self) -> Expr:
    expr: Expr = self._or()
    if self._match(TokenType.EQUAL):
      equals: Token = self._previous()
      value: Expr = self._assignment() # recursively parse the right-hand side.

      if isinstance(expr, Variable):
        name: Token = expr.name 
        return Assign(name, value)
      else:
        """
        Report an error, but don't raise it because the parser isn't 
        in a confused state that requires going into panic mode
        and synchronizing.
        """
        self._error(equals, "Invalid assignment target.")
    return expr

  """
  Implements Grammar Rule
  logic_or -> logic_and ( "or" logic_and )*;
  """
  def _or(self) -> Expr:
    expr: Expr = self._and()
    while self._match(TokenType.OR):
      operator: Token = self._previous()
      right: Expr = self._and()
      expr = LogicalExpr(expr, operator, right)
    return expr 

  """
  Implements Grammar Rule
  logic_and   -> equality ( "and" equality )*;
  """
  def _and(self) -> Expr:
    expr: Expr = self._equality()
    while self._match(TokenType.AND):
      operator: Token = self._previous()
      right: Expr = self._equality()
      expr = LogicalExpr(expr, operator, right)
    return expr 
    
  """
  Implements Grammar Rule
  statement -> exprStmt | ifStmt | blockStmt | printStmt | clearStmt | historyStmt; 
  """
  def _statement(self) -> Stmt:
    if self._match(TokenType.IF):
      return self._if_statement()

    if self._match(TokenType.LEFT_BRACE):
      return Block(self._block())

    if self._match(TokenType.PRINT):
      return self._print_statement()
    
    if self._match(TokenType.CLEAR):
      return self._clear_statement()
    
    if self._match(TokenType.HISTORY):
      return self._history_statement()
    
    return self._expression_statement()

  """
  Implements Grammar Rule
  ifStmt  -> "if" "(" expression ")" statement
              ( "else" statement )? ;
  """
  def _if_statement(self) -> Stmt:
    self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
    condition: Expr = self._expression()
    self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

    then_branch: Stmt = self._statement()
    else_branch: Stmt = None
    if self._match(TokenType.ELSE):
      else_branch = self._statement()
    return If(condition, then_branch, else_branch)
  """
  Implements Grammar Rule
  blockStmt -> "{" declaration* "}" ;
  """
  def _block(self) -> List[Stmt]:
    statements: List[Stmt] = []
    while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
      statements.append(self._declaration())
    self._consume(TokenType.RIGHT_BRACE, "Expect '}' after code block.")
    return statements

  def _expression_statement(self) -> Stmt:
    value: Expr = self._expression()
    self._consume(TokenType.SEMICOLON, "A ';' is required at the end of a statement.")
    return Expression(value)
  
  def _print_statement(self) -> Stmt:
    value: Expr = self._expression()
    self._consume(TokenType.SEMICOLON, "A ';' is required at the end of a statement.")
    return Print(value)
  
  def _clear_statement(self) -> Stmt:
    self._consume(TokenType.SEMICOLON, "A ';' is required at the end of a statement.")
    return Clear()
  
  def _history_statement(self) -> Stmt:
    self._consume(TokenType.SEMICOLON, "A ';' is required at the end of a statement.")
    return History()

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
  primary -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" | IDENTIFIER;
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
    elif self._match(TokenType.IDENTIFIER):
      return Variable(self._previous())

  def _consume(self, type: TokenType, error_msg: str) -> Token:
    if self._check(type):
      return self._advance()
    else:
      print(self._tokens)
      raise self._error(self._peek(), error_msg)

  def _error(self, token: Token, error_msg: str) -> ParseError:
    self._handle_error(token, error_msg)
    return ParseError(token, error_msg)

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
