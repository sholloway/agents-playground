"""
This modules defines the Abstract Syntax Tree for the terminal language.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, List, TypeVar
from agents_playground.terminal.token import Token

"""
Abstract Syntax (pg65)
expression  -> literal | unary | binary | grouping;
literal     -> NUMBER | STRING | "true" | "false" | "nil";
grouping    -> "(" expression ")";
unary       -> ( "-" | "!" ) expression;
binary      -> expression operator expression;
operator    -> "==" | "!=" | "<" | "<=" | ">" | ">=" | "+" | "-" | "*" | "/";
"""

VisitorResult = TypeVar("VisitorResult")

class Expression(ABC):
  def __init__(self) -> None:
    pass

  @abstractmethod
  def accept(self, visitor: Visitor) -> VisitorResult:
    """"""

class Visitor(ABC, Generic[VisitorResult]):
  @abstractmethod
  def visit_binary_expr(self, expression: BinaryExpr) -> VisitorResult:
    """Handle visiting a binary expression."""
  
  @abstractmethod
  def visit_grouping_expr(self, expression: GroupingExpr) -> VisitorResult:
    """Handle visiting a grouping expression."""
  
  @abstractmethod
  def visit_literal_expr(self, expression: LiteralExpr) -> VisitorResult:
    """Handle visiting a literal expression."""
  
  @abstractmethod
  def visit_unary_expr(self, expression: UnaryExpr) -> VisitorResult:
    """Handle visiting a unary expression."""

class InlineASTFormatter(Visitor[str]):
  def _parenthesize(self, name: str, *expressions: Expression) -> str:
    result = f'({name}'

    for expr in expressions:
      result += ' '
      result += expr.accept(self)
    
    result += ')'
    return result

  """Given the root of an AST, formats a string suitable for printing."""
  def format(self, expression: Expression) -> str:
    return expression.accept(self)

  def visit_binary_expr(self, expression: BinaryExpr) -> str:
    """Handle visiting a binary expression."""
    return self._parenthesize(expression.operator.lexeme, expression.left, expression.right)
  
  def visit_grouping_expr(self, expression: GroupingExpr) -> str:
    """Handle visiting a grouping expression."""
    return self._parenthesize('group', expression.expression)
  
  def visit_literal_expr(self, expression: LiteralExpr) -> str:
    """Handle visiting a literal expression."""
    if expression.value is None:
      return 'None'
    return str(expression.value)
  
  def visit_unary_expr(self, expression: UnaryExpr) -> str:
    """Handle visiting a unary expression."""
    return self._parenthesize(expression.operator.lexeme, expression.right)

class BinaryExpr(Expression):
  def __init__(self, left: Expression, operator: Token, right: Expression) -> None:
    super().__init__()
    self.left = left 
    self.operator = operator
    self.right = right

  def accept(self, visitor: Visitor) -> VisitorResult:
    return visitor.visit_binary_expr(self)

class GroupingExpr(Expression):
  def __init__(self, expression: Expression) -> None:
    super().__init__()
    self.expression = expression

  def accept(self, visitor: Visitor) -> VisitorResult:
    return visitor.visit_grouping_expr(self)

class LiteralExpr(Expression):
  def __init__(self, value: Any) -> None:
    super().__init__()
    self.value = value 

  def accept(self, visitor: Visitor) -> VisitorResult:
    return visitor.visit_literal_expr(self)

class UnaryExpr(Expression):
  def __init__(self, operator: Token, right: Expression) -> None:
    super().__init__()
    self.operator = operator
    self.right = right

  def accept(self, visitor: Visitor) -> VisitorResult:
    return visitor.visit_unary_expr(self)