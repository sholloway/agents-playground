
from typing import Any

import pytest

from agents_playground.terminal.ast import Expr
from agents_playground.terminal.interpreter import Interpreter, InterpreterRuntimeError
from agents_playground.terminal.lexer import Lexer
from agents_playground.terminal.parser import Parser


class TestInterpreter:
  def setup_class(self) -> None:
    self.lexer = Lexer()
    self.interpreter = Interpreter()

  def interpret(self, user_input: str) -> Any:
    tokens = self.lexer.scan(user_input)
    parser = Parser(tokens)
    expr: Expr = parser.parse()
    return self.interpreter.interpret(expr)

  def test_literal_expressions(self) -> None:
    assert 1978 == self.interpret('1978')
    assert 1 == self.interpret('1')
    assert True == self.interpret('True')
    assert False == self.interpret('False')
    assert 'Hello World' == self.interpret('\'Hello World\'')
    assert 'Hello World' == self.interpret('"Hello World"')
    assert self.interpret('None') is None 

  def test_unary_expressions(self) -> None:
    assert -1 == self.interpret('-1')
    assert False == self.interpret('!True')
    assert True == self.interpret('!False')

  def test_operators(self) -> None:
    assert True   == self.interpret('1 == 1')
    assert False  == self.interpret('1 == 2')
    
    assert True   == self.interpret('1 != 2')
    assert False  == self.interpret('1 != 1')

    assert True   == self.interpret('1 < 2')
    assert False  == self.interpret('1 < 0')
    
    assert True   == self.interpret('1 <= 2')
    assert True   == self.interpret('1 <= 1')
    assert False  == self.interpret('1 <= 0')
    
    assert True   == self.interpret('1 > 0')
    assert False  == self.interpret('1 > 1')
    
    assert True   == self.interpret('1 >= 0')
    assert True   == self.interpret('1 >= 1')
    assert False   == self.interpret('1 >= 2')

    assert 3    == self.interpret('1 + 2')
    assert 0    == self.interpret('1 - 1')
    assert 0    == self.interpret('1 * 0')
    assert 28   == self.interpret('14 * 2')
    assert 2.50 == self.interpret('1.25 * 2')
    
    assert 1  == self.interpret('7/7.0')
    assert 2.5  == self.interpret('5/2')
    

  def test_divide_by_zero(self) -> None:
    with pytest.raises(InterpreterRuntimeError, match='Cannot divide by zero.'):
      self.interpret('1/0')

  def test_grouping(self) -> None:
    assert 1 == self.interpret('(1)')
    assert 2 == self.interpret('(1 + 1)')
    assert 3 == self.interpret('(1 + 1 + 1)')
    assert 10 == self.interpret('(1) + (1 + 1) + (1 + 1 + 1) + (1 + 1 + 1 + 1)')

  def test_numeric_expressions(self) -> None:
    assert 94 == self.interpret('2 * (42 + 5)')
    assert 2.5714285714285716 == self.interpret('(4 + 17 - 3)/(14/2)')
    assert 29.6 == self.interpret('((1043 + 9) - (304 * 2))/(9 + 8 - 2)')
    