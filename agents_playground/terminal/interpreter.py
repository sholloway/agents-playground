from abc import ABC, abstractmethod, abstractproperty
from typing import List
from agents_playground.terminal.ast.statements import Stmt

from agents_playground.terminal.environment import Environment

class Interpreter(ABC):
  @abstractproperty
  def globals(self) -> Environment:
    """Property that returns the global environment."""
  
  @abstractmethod
  def execute_block(self, statements: List[Stmt], local_environment: Environment) -> None:
    """Run a list of statements."""
  

