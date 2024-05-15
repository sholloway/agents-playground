from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, List, TypeVar
from agents_playground.terminal.ast.visitor_result_type import VisitorResult
from agents_playground.terminal.token import Token


class Expr(ABC, Generic[VisitorResult]):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def accept(self, visitor: ExprVisitor) -> VisitorResult:
        """"""


class ExprVisitor(ABC, Generic[VisitorResult]):
    @abstractmethod
    def visit_logical_expr(
        self, expression: LogicalExpr[VisitorResult]
    ) -> VisitorResult:
        """Handle visiting a logical expression."""

    @abstractmethod
    def visit_binary_expr(self, expression: BinaryExpr[VisitorResult]) -> VisitorResult:
        """Handle visiting a binary expression."""

    @abstractmethod
    def visit_call_expr(self, expression: Call[VisitorResult]) -> VisitorResult:
        """Handle visiting a call expression."""

    @abstractmethod
    def visit_grouping_expr(
        self, expression: GroupingExpr[VisitorResult]
    ) -> VisitorResult:
        """Handle visiting a grouping expression."""

    @abstractmethod
    def visit_literal_expr(
        self, expression: LiteralExpr[VisitorResult]
    ) -> VisitorResult:
        """Handle visiting a literal expression."""

    @abstractmethod
    def visit_unary_expr(self, expression: UnaryExpr[VisitorResult]) -> VisitorResult:
        """Handle visiting a unary expression."""

    @abstractmethod
    def visit_variable_expr(self, expression: Variable[VisitorResult]) -> VisitorResult:
        """Handle visiting a variable."""

    @abstractmethod
    def visit_assign_expr(self, expression: Assign[VisitorResult]) -> VisitorResult:
        """Handle visiting an assignment."""


class BinaryExpr(Expr, Generic[VisitorResult]):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor[VisitorResult]) -> VisitorResult:
        return visitor.visit_binary_expr(self)


class Call(Expr, Generic[VisitorResult]):
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]) -> None:
        super().__init__()
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: ExprVisitor[VisitorResult]) -> VisitorResult:
        return visitor.visit_call_expr(self)


class GroupingExpr(Expr, Generic[VisitorResult]):
    def __init__(self, expression: Expr) -> None:
        super().__init__()
        self.expression = expression

    def accept(self, visitor: ExprVisitor[VisitorResult]) -> VisitorResult:
        return visitor.visit_grouping_expr(self)


class LiteralExpr(Expr, Generic[VisitorResult]):
    def __init__(self, value: Any) -> None:
        super().__init__()
        self.value = value

    def accept(self, visitor: ExprVisitor[VisitorResult]) -> VisitorResult:
        return visitor.visit_literal_expr(self)


class LogicalExpr(Expr, Generic[VisitorResult]):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor[VisitorResult]) -> VisitorResult:
        return visitor.visit_logical_expr(self)


class UnaryExpr(Expr, Generic[VisitorResult]):
    def __init__(self, operator: Token, right: Expr) -> None:
        super().__init__()
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor[VisitorResult]) -> VisitorResult:
        return visitor.visit_unary_expr(self)


class Variable(Expr, Generic[VisitorResult]):
    def __init__(self, name: Token) -> None:
        super().__init__()
        self.name = name

    def accept(self, visitor: ExprVisitor[VisitorResult]) -> VisitorResult:
        return visitor.visit_variable_expr(self)


class Assign(Expr, Generic[VisitorResult]):
    def __init__(self, name: Token, value: Expr) -> None:
        super().__init__()
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor[VisitorResult]) -> VisitorResult:
        return visitor.visit_assign_expr(self)
