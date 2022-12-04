from unittest.mock import Mock as UnitTestMock
from pytest_mock import MockFixture

from typing import Any, List

import pytest
from agents_playground.terminal.ast.expressions import Expr
from agents_playground.terminal.ast.statements import Stmt

from agents_playground.terminal.interpreter import Interpreter, InterpreterRuntimeError
from agents_playground.terminal.lexer import Lexer
from agents_playground.terminal.parser import Parser
from agents_playground.terminal.terminal_buffer import TerminalBuffer
from agents_playground.terminal.terminal_display import TerminalDisplay
from agents_playground.terminal.token import Token
from agents_playground.terminal.token_type import TokenType

class TestInterpreter:
  def setup_class(self) -> None:
    self.lexer = Lexer()
    self.terminal_buffer = TerminalBuffer()
    self.terminal_display = UnitTestMock()
    self.interpreter = Interpreter(self.terminal_buffer, self.terminal_display)

  def interpret(self, user_input: str) -> Any:
    """This is a helper method to simplify the tests."""
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
    
  def test_print_statement(self) -> None:
    tokens = self.lexer.scan('print "hello world";')
    parser = Parser(tokens)
    statements: List[Stmt] = parser.parse()
    self.terminal_buffer.clear()
    self.interpreter.interpret(statements)
    # Assert that hello world was printed. (Including the > character.)
    assert '\ue285 hello world' in self.terminal_buffer._scroll_back_buffer
  
  def test_history_statement(self) -> None:
    tokens = self.lexer.scan('history;')
    parser = Parser(tokens)
    statements: List[Stmt] = parser.parse()
    self.interpreter.interpret(statements)

  def test_assignment(self, mocker: MockFixture) -> None:
    lexer = Lexer()
    terminal_buffer = TerminalBuffer()
    terminal_display = mocker.Mock()
    interpreter = Interpreter(terminal_buffer, terminal_display)

    tokens = lexer.scan('var a = 1;')
    parser = Parser(tokens)
    statements: List[Stmt] = parser.parse()

    a_token: Token = Token(TokenType.IDENTIFIER, lexeme='a', literal=None, line=0)
    assert not (a_token.lexeme in interpreter._environment._in_memory_values)
    interpreter.interpret(statements)
    assert a_token.lexeme in interpreter._environment._in_memory_values
    assert interpreter._environment.get(a_token) == 1