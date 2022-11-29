
from numbers import Number
from typing import Any, List

from agents_playground.terminal.ast import (
  BinaryExpr,
  Expr,
  Expression, 
  GroupingExpr, 
  LiteralExpr,
  Stmt,
  StmtVisitor, 
  UnaryExpr, 
  ExprVisitor
)
from agents_playground.terminal.terminal_buffer import TerminalBuffer
from agents_playground.terminal.terminal_display import TerminalDisplay
from agents_playground.terminal.token import Token
from agents_playground.terminal.token_type import TokenType

class InterpreterRuntimeError(Exception):
  def __init__(self, token: Token, *args: object) -> None:
    super().__init__(*args)
    self._token = token

class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
  def __init__(self, buffer: TerminalBuffer, display: TerminalDisplay) -> None:
    super().__init__()
    self._terminal_buffer = buffer
    self._terminal_display = display

  def interpret(self, statements: List[Stmt]) -> None:
    try:
      for statement in statements:
        self._execute(statement)
    except InterpreterRuntimeError as re:
      # TODO: Probably need to do more with error handling here.
      raise re

  def _execute(self, stmt: Stmt):
    stmt.accept(self)

  def _evaluate(self, expression: Expr) -> Any:
    return expression.accept(self)

  def visit_expression_stmt(self, stmt: Expression) -> None:
    """Handle visiting an expression statement."""
    self._evaluate(stmt.expression)
    return
  
  def visit_print_stmt(self, stmt: Expression) -> None:
    """Handle visiting a print statement."""
    value: Any = self._evaluate(stmt.expression)
    self._terminal_buffer.append_output(f'{chr(0xE285)} {str(value)}', remember=False)
    self._terminal_display.refresh(self._terminal_buffer)
    return

  
  def visit_clear_stmt(self, stmt: Expression) -> None:
    """Handle visiting a 'clear' statement."""
    self._terminal_buffer.clear()
    self._terminal_display.refresh(self._terminal_buffer)
    return
  
  def visit_history_stmt(self, stmt: Expression) -> None:
    self._terminal_buffer.append_output(
      self._terminal_buffer.history(), 
      remember=False
    )
    self._terminal_display.refresh(self._terminal_buffer)

  def _truth_value(self, value: Any) -> bool:
    """Returns the truth value (True/False) of an expression.
    
    The truth rules are:
    1. None -> False
    2. Boolean values return their value.
    3. 0 | 0.0 -> False
    4. 1 | 1.0 -> True
    3. Anything that is assigned (e.g. x = 'abc') returns true.
    """
    match value:
      case None:
        return False
      case bool(_):
        return value
      case 0 | 0.0:
        return False
      case 1 | 1.0:
        return True
      case _:
        return True

  def _is_equal(self, left: Any, right: Any) -> bool:
    """Determine if two values are equal."""
    # For now, use the same equality rules as Python.
    return left == right

  def _check_number_operand(self, operator: Token, operand: Any) -> None:
    if isinstance(operand, Number):
      return
    else:
      raise InterpreterRuntimeError(operator, 'Operand must be a number.')
  
  def _check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
    if isinstance(left, Number) and isinstance(right, Number):
      return
    else:
      raise InterpreterRuntimeError(operator, 'Operands must both be numbers.')
    
  def _enforce_no_divide_by_zero(self, operator: Token, possible_number: Any) -> None:
    if isinstance(possible_number, Number) and possible_number == 0:
      raise InterpreterRuntimeError(operator, 'Cannot divide by zero.')

  def visit_binary_expr(self, expression: BinaryExpr) -> Any:
    """Handle visiting a binary expression."""
    # 1. First evaluate the left side of the expression and then the right side.
    left:  Any = self._evaluate(expression.left)
    right: Any = self._evaluate(expression.right)

    # 2. Evaluate the binary operand by applying it to the results of the left and right.
    match expression.operator.type:
      case TokenType.MINUS:
        self._check_number_operands(expression.operator, left, right)
        return float(left) - float(right)
      case TokenType.PLUS: # Plus can both add numbers and concatenate strings.
        if isinstance(left, Number) and isinstance(right, Number):
          # Handle adding two numbers.
          # Note: The values True/False will be converted to 1/0.
          return float(left) + float(right)
        elif  (isinstance(left, str)    or isinstance(right, str)) and \
              (isinstance(left, Number) or isinstance(right, Number)):
          # If either the left or right is a string create a new string by joining the values.
          return str(left) + str(right)
        else:
          raise InterpreterRuntimeError(expression.operator, 'Operands must be a combination of numbers and strings.')
      case TokenType.SLASH:
        self._check_number_operands(expression.operator, left, right)
        self._enforce_no_divide_by_zero(expression.operator, right)
        return float(left)/float(right)
      case TokenType.STAR:
        self._check_number_operands(expression.operator, left, right)
        return float(left) * float(right)
      case TokenType.GREATER:
        self._check_number_operands(expression.operator, left, right)
        return left > right
      case TokenType.GREATER_EQUAL:
        self._check_number_operands(expression.operator, left, right)
        return left >= right
      case TokenType.LESS:
        self._check_number_operands(expression.operator, left, right)
        return left < right
      case TokenType.LESS_EQUAL:
        self._check_number_operands(expression.operator, left, right)
        return left <= right
      case TokenType.BANG_EQUAL:
        return not self._is_equal(left,right)
      case TokenType.EQUAL_EQUAL:
        return self._is_equal(left,right)
      case _:
        # shouldn't get here.
        # TODO: Throw an error.
        return None
  
  def visit_grouping_expr(self, expression: GroupingExpr) -> Any:
    """Handle visiting a grouping expression."""
    return self._evaluate(expression.expression)
  
  def visit_literal_expr(self, expression: LiteralExpr) -> Any:
    """Handle visiting a literal expression."""
    return expression.value
  
  def visit_unary_expr(self, expression: UnaryExpr) -> Any:
    """Handle visiting a unary expression."""
    # 1. First evaluate the right side of the expression
    right: Any  = self._evaluate(expression.right)

    # 2. Evaluate the unary operator.
    match expression.operator.type:
      case TokenType.BANG:
        return not self._truth_value(right)
      case TokenType.MINUS:
        self._check_number_operand(expression.operator, right)
        return -float(right)

    # This should be unreachable.
    # TODO: Throw an error rather than return None.
    return None