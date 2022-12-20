from collections import deque
from enum import auto, Enum
from typing import Any, Deque, Dict, List, Tuple
from agents_playground.terminal.ast.expressions import Assign, BinaryExpr, Call, Expr, ExprVisitor, GroupingExpr, LiteralExpr, LogicalExpr, UnaryExpr, Variable
from agents_playground.terminal.ast.statements import Block, Clear, Expression, Function, History, If, Print, Return, Stmt, StmtVisitor, Var, While
from agents_playground.terminal.ast.visitor_result_type import VisitorResult
from agents_playground.terminal.interpreter import Interpreter
from agents_playground.terminal.token import Token

class FunctionType(Enum):
  NONE     = auto()
  FUNCTION = auto()

class Resolver(ExprVisitor[Any], StmtVisitor[None]):
  def __init__(self, interpreter: Interpreter) -> None:
    super().__init__()
    self._interpreter = interpreter
    self._scopes: Deque[Dict[str, bool]] = deque()
    self._current_function: FunctionType = FunctionType.NONE
    self._encountered_error: bool = False
    self._errors: List[Tuple[Token, str]] = []

  def encounter_errors(self) -> bool:
    return self._encountered_error

  def _error(self, token: Token, msg: str) -> None:
    self._encountered_error = True
    self._errors.append((token, msg))

  def visit_block_stmt(self, block: Block) -> None:
    self._begin_scope()
    self.resolve(block.statements)
    self._end_scope()
    return None

  def visit_var_declaration(self, stmt: Var) -> None:
    self._declare(stmt.name)
    if stmt.initializer is not None:
      self._resolve_stmt(stmt.initializer)
    self._define(stmt.name)
    return None

  def visit_variable_expr(self, expr: Variable) -> None:
    if len(self._scopes) > 0 and self._scopes[len(self._scopes) -1 ].get(expr.name.lexeme) == False:
      self._error(expr.name, 'Cannot read local variable in its own initializer.')
    self._resolve_local(expr, expr.name)
    return None

  def visit_assign_expr(self, expr: Assign) -> None:
    self._resolve_expr(expr.value)
    self._resolve_local(expr, expr.name)
    return None

  def visit_function_stmt(self, stmt: Function) -> None:
    self._declare(stmt.name)
    self._define(stmt.name)
    self._resolve_function(stmt, FunctionType.FUNCTION)
    return None

  def visit_expression_stmt(self, stmt: Expression) -> None:
    self._resolve_expr(stmt.expression)
    return None

  def visit_if_statement(self, stmt: If) -> None:
    self._resolve_stmt(stmt.condition)
    self._resolve_stmt(stmt.then_branch)
    if stmt.else_branch is not None:
      self._resolve_stmt(stmt.else_branch)
    return None

  def visit_print_stmt(self, stmt: Print) -> None:
    self._resolve_stmt(stmt.expression)
    return None

  def visit_clear_stmt(self, stmt: Clear) -> None:
    return None

  def visit_history_stmt(self, stmt: History) -> None:
    return None

  def visit_return_stmt(self, stmt: Return) -> None:
    if self._current_function == FunctionType.NONE:
      self._error(stmt.keyword, "Cannot return from top-level code.")
    if stmt.value is not None:
      self._resolve_expr(stmt.value)
    return None

  def visit_while_statement(self, stmt: While) -> None:
    self._resolve_expr(stmt.condition)
    self.resolve(stmt.body)
    return None

  def visit_binary_expr(self, expr: BinaryExpr) -> None:
    self._resolve_expr(expr.left)
    self._resolve_expr(expr.right)
    return None

  def visit_call_expr(self, expr: Call) -> FileNotFoundError:
    self._resolve_expr(expr.callee)
    arg: Expr
    for arg in expr.arguments:
      self._resolve_expr(arg)
    return None

  def visit_grouping_expr(self, expr: GroupingExpr) -> None:
    self._resolve_expr(expr.expression)
    return None

  def visit_literal_expr(self, expr: LiteralExpr) -> None:
    return None

  def visit_logical_expr(self, expr: LogicalExpr) -> None:
    self._resolve_expr(expr.left)
    self._resolve_expr(expr.right)
    return None

  def visit_unary_expr(self, expr: UnaryExpr) -> None:
    self._resolve_expr(expr.right)

  def _declare(self, name: Token) -> None:
    if len(self._scopes) == 0:
      return None
    scope: Dict[str, bool] = self._scopes[len(self._scopes) -1 ] # TODO: need a peek function
    if name.lexeme in scope:
      self._error(name, "Already a variable with this name in this scope.")
    scope[name.lexeme] = False

  def _define(self, name: Token) -> None:
    if len(self._scopes) == 0:
      return None
    scope: Dict[str, bool] = self._scopes[len(self._scopes) -1 ] # TODO: need a peek function
    scope[name.lexeme] = True

  def _begin_scope(self) -> None:
    scope: Dict[str, bool] = {}
    self._scopes.append(scope)
    return None

  def _end_scope(self) -> None:
    self._scopes.pop()
    return None

  def resolve(self, statements: List[Stmt]) -> None:
    statement: Stmt
    for statement in statements:
      self._resolve_stmt(statement)
    return None

  def _resolve_stmt(self, statement: Stmt) -> None:
    statement.accept(self) 

  def _resolve_expr(self, expression: Expr) -> None:
    expression.accept(self)

  def _resolve_local(self, expr: Expression, name: Token) -> None:
    for index in range(len(self._scopes) - 1, -1, step = -1):
      if name.lexeme in self._scopes[index]:
        self._interpreter.resolve(expr, len(self._scopes) - 1 - index) 
        return

  def _resolve_function(self, function: Function, func_type: FunctionType) -> None:
    enclosing_function = self._current_function
    self._current_function = func_type
    self._begin_scope()
    for param in function.params:
      self._declare(param)
      self._define(param)
    self.resolve(function.body)
    self._end_scope()
    self._current_function = enclosing_function