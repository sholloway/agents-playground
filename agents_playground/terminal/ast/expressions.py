from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from agents_playground.terminal.ast.visitor_result_type import VisitorResult
from agents_playground.terminal.token import Token

class Expr(ABC):
  def __init__(self) -> None:
    pass

  @abstractmethod
  def accept(self, visitor: ExprVisitor) -> VisitorResult:
    """"""

class ExprVisitor(ABC, Generic[VisitorResult]):
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

  @abstractmethod
  def visit_variable_expr(self, expression: Variable) -> VisitorResult:
    """Handle visiting a variable."""

  @abstractmethod
  def visit_assign_expr(self, expression: Assign) -> VisitorResult:
    """Handle visiting an assignment."""

class BinaryExpr(Expr):
  def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
    super().__init__()
    self.left = left 
    self.operator = operator
    self.right = right

  def accept(self, visitor: ExprVisitor) -> VisitorResult:
    return visitor.visit_binary_expr(self)

class GroupingExpr(Expr):
  def __init__(self, expression: Expr) -> None:
    super().__init__()
    self.expression = expression

  def accept(self, visitor: ExprVisitor) -> VisitorResult:
    return visitor.visit_grouping_expr(self)

class LiteralExpr(Expr):
  def __init__(self, value: Any) -> None:
    super().__init__()
    self.value = value 

  def accept(self, visitor: ExprVisitor) -> VisitorResult:
    return visitor.visit_literal_expr(self)

class UnaryExpr(Expr):
  def __init__(self, operator: Token, right: Expr) -> None:
    super().__init__()
    self.operator = operator
    self.right = right

  def accept(self, visitor: ExprVisitor) -> VisitorResult:
    return visitor.visit_unary_expr(self)
  
class Variable(Expr):
  def __init__(self, name: Token) -> None:
    super().__init__()
    self.name = name

  def accept(self, visitor: ExprVisitor) -> VisitorResult:
    return visitor.visit_variable_expr(self)  

class Assign(Expr):
  def __init__(self, name: Token, value: Expr) -> None:
    super().__init__()
    self.name = name
    self.value = value
  
  def accept(self, visitor: ExprVisitor) -> VisitorResult:
    return visitor.visit_assign_expr(self)