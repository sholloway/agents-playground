from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, List
from agents_playground.terminal.ast.expressions import Expr
from agents_playground.terminal.ast.visitor_result_type import VisitorResult
from agents_playground.terminal.token import Token

class Stmt(ABC):
  def __init__(self) -> None:
    pass

  @abstractmethod
  def accept(self, visitor: StmtVisitor) -> VisitorResult:
    """"""

class StmtVisitor(ABC, Generic[VisitorResult]):
  @abstractmethod
  def visit_if_statement(self, is_stmt: If) -> VisitorResult:
    """Handle visiting an if statement."""
  
  @abstractmethod
  def visit_while_statement(self, while_stmt: While) -> VisitorResult:
    """Handle visiting a while statement."""

  @abstractmethod
  def visit_block_stmt(self, block: Block) -> VisitorResult:
    """Handle visiting a block of statements."""
  
  @abstractmethod
  def visit_var_declaration(self, stmt: Var) -> VisitorResult:
    """Handle visiting a variable declaration statement."""

  @abstractmethod
  def visit_expression_stmt(self, stmt: Expression) -> VisitorResult:
    """Handle visiting an expression statement."""
  
  @abstractmethod
  def visit_print_stmt(self, stmt: Print) -> VisitorResult:
    """Handle visiting a print statement."""
  
  @abstractmethod
  def visit_clear_stmt(self, stmt: Clear) -> VisitorResult:
    """Handle visiting a 'clear' statement."""
  
  @abstractmethod
  def visit_history_stmt(self, stmt: History) -> VisitorResult:
    """Handle visiting a 'history' statement."""


class Block(Stmt):
  def __init__(self, statements: List[Stmt]) -> None:
    super().__init__()
    self.statements = statements

  def accept(self, visitor: StmtVisitor) -> VisitorResult:
    return visitor.visit_block_stmt(self)

class Expression(Stmt):
  def __init__(self, expression: Expr) -> None:
    super().__init__()
    self.expression = expression

  def accept(self, visitor: StmtVisitor) -> VisitorResult:
    return visitor.visit_expression_stmt(self)
  
class If(Stmt):
  def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt) -> None:
    super().__init__()
    self.condition = condition
    self.then_branch = then_branch
    self.else_branch = else_branch

  def accept(self, visitor: StmtVisitor) -> VisitorResult:
    return visitor.visit_if_statement(self)

class While(Stmt):
  def __init__(self, condition: Expr, body: Stmt) -> None:
    super().__init__()
    self.condition = condition
    self.body = body 

  def accept(self, visitor: StmtVisitor) -> VisitorResult:
    return visitor.visit_while_statement(self) 

class Var(Stmt):
  def __init__(self, name: Token, initializer:Expression) -> None:
    super().__init__()
    self.name = name
    self.initializer = initializer
  
  def accept(self, visitor: StmtVisitor) -> VisitorResult:
    return visitor.visit_var_declaration(self)

class Print(Stmt):
  def __init__(self, expression: Expr) -> None:
    super().__init__()
    self.expression = expression

  def accept(self, visitor: StmtVisitor) -> VisitorResult:
    return visitor.visit_print_stmt(self)

class Clear(Stmt):
  def __init__(self) -> None:
    super().__init__()

  def accept(self, visitor: StmtVisitor) -> VisitorResult:
    return visitor.visit_clear_stmt(self)

class History(Stmt):
  def __init__(self) -> None:
    super().__init__()

  def accept(self, visitor: StmtVisitor) -> VisitorResult:
    return visitor.visit_history_stmt(self)