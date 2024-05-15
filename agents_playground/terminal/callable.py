from abc import ABC, abstractmethod
from typing import Any, List

from agents_playground.terminal.interpreter import Interpreter


class Callable(ABC):
    @abstractmethod
    def call(self, interpreter: Interpreter, args: List[Any]) -> Any:
        """Handle invoking a function call."""

    @abstractmethod
    def arity(self) -> int:
        """Returns the number of required arguments."""
