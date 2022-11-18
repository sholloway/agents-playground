
from numbers import Number
from typing import Any
from agents_playground.terminal.ast import (
  BinaryExpr,
  Expression, 
  GroupingExpr, 
  LiteralExpr, 
  UnaryExpr, 
  Visitor
)
from agents_playground.terminal.token_type import TokenType

class Interpreter(Visitor[Any]):
  def _evaluate(self, expression: Expression) -> Any:
    return expression.accept(self)

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

  def _is_equal(left: Any, right: Any) -> bool:
    """Determine if two values are equal."""
    # For now, use the same equality rules as Python.
    return left == right
    
  def visit_binary_expr(self, expression: BinaryExpr) -> Any:
    """Handle visiting a binary expression."""
    # 1. First evaluate the left side of the expression and then the right side.
    left:  Any = self._evaluate(expression.left)
    right: Any = self._evaluate(expression.right)

    # 2. Evaluate the binary operand by applying it to the results of the left and right.
    match expression.operator.type:
      case TokenType.MINUS:
        return float(left) - float(right)
      case TokenType.PLUS: # Plus can both add numbers and concatenate strings.
        if isinstance(left, Number) and isinstance(right, Number):
          # Handle adding two numbers.
          # Note: The values True/False will be converted to 1/0.
          return float(left) + float(right)
        elif isinstance(left, str) or isinstance(right, str):
          # If either the left or right is a string create a new string by joining the values.
          return str(left) + str(right)
      case TokenType.SLASH:
        return float(left)/float(right)
      case TokenType.STAR:
        return float(left) * float(right)
      case TokenType.GREATER:
        return left > right
      case TokenType.GREATER_EQUAL:
        return left >= right
      case TokenType.LESS:
        return left < right
      case TokenType.LESS_EQUAL:
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
        return -float(right)

    # This should be unreachable.
    # TODO: Throw an error rather than return None.
    return None