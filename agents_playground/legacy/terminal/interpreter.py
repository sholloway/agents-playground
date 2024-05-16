from abc import ABC, abstractmethod, abstractproperty
from typing import List
from agents_playground.legacy.terminal.ast.expressions import Expr
from agents_playground.legacy.terminal.ast.statements import Stmt

from agents_playground.legacy.terminal.environment import Environment


class Interpreter(ABC):
    @abstractproperty
    def globals(self) -> Environment:
        """Property that returns the global environment."""

    @abstractmethod
    def execute_block(
        self, statements: List[Stmt], local_environment: Environment
    ) -> None:
        """Run a list of statements."""

    @abstractmethod
    def resolve(self, expr: Expr, depth: int) -> None:
        """Resolve an expression's variables."""
