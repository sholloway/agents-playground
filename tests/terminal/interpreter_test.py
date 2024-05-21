import pytest
from unittest.mock import Mock as UnitTestMock
from pytest_mock import MockFixture

from typing import Any, List

import pytest
from agents_playground.legacy.terminal.ast.expressions import Expr
from agents_playground.legacy.terminal.ast.statements import Stmt
from agents_playground.legacy.terminal.resolver import Resolver

from agents_playground.legacy.terminal.terminal_interpreter import TerminalInterpreter
from agents_playground.legacy.terminal.interpreter_runtime_error import (
    InterpreterRuntimeError,
)
from agents_playground.legacy.terminal.lexer import Lexer
from agents_playground.legacy.terminal.parser import Parser
from agents_playground.legacy.terminal.terminal_buffer import (
    TerminalBuffer,
    TerminalBufferUserInput,
)
from agents_playground.legacy.terminal.terminal_display import TerminalDisplay
from agents_playground.legacy.terminal.token import Token
from agents_playground.legacy.terminal.token_type import TokenType


def assert_in_outputted_to_buffer(code: str, output: str):
    lexer = Lexer()
    terminal_buffer = TerminalBuffer()
    terminal_display = UnitTestMock()
    interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

    tokens = lexer.scan(code)
    parser = Parser(tokens)
    statements: List[Stmt] = parser.parse()
    interpreter.interpret(statements)
    output_msgs: List[str] = list(
        map(lambda l: l.raw_content(), terminal_buffer.output())
    )
    assert output in output_msgs, f"{output} was not found in the scroll back buffer."


class TestInterpreter:
    def test_literal_expressions(self, mocker: MockFixture) -> None:
        assert_in_outputted_to_buffer("1;", "1")
        assert_in_outputted_to_buffer("1978;", "1978")
        assert_in_outputted_to_buffer("True;", "True")
        assert_in_outputted_to_buffer("False;", "False")
        assert_in_outputted_to_buffer("'Hello World';", "Hello World")
        assert_in_outputted_to_buffer('"Hello World";', "Hello World")
        assert_in_outputted_to_buffer("None;", "None")

    def test_unary_expressions(self) -> None:
        assert_in_outputted_to_buffer("-1;", "-1.0")
        assert_in_outputted_to_buffer("!True;", "False")
        assert_in_outputted_to_buffer("!False;", "True")

    def test_operators(self) -> None:
        assert_in_outputted_to_buffer("1 == 1;", "True")
        assert_in_outputted_to_buffer("1 == 2;", "False")

        assert_in_outputted_to_buffer("1 != 2;", "True")
        assert_in_outputted_to_buffer("1 != 1;", "False")

        assert_in_outputted_to_buffer("1 < 2;", "True")
        assert_in_outputted_to_buffer("1 < 0;", "False")

        assert_in_outputted_to_buffer("1 <= 2;", "True")
        assert_in_outputted_to_buffer("1 <= 1;", "True")
        assert_in_outputted_to_buffer("1 <= 0;", "False")

        assert_in_outputted_to_buffer("1 > 0;", "True")
        assert_in_outputted_to_buffer("1 > 1;", "False")

        assert_in_outputted_to_buffer("1 >= 0;", "True")
        assert_in_outputted_to_buffer("1 >= 1;", "True")
        assert_in_outputted_to_buffer("1 >= 2;", "False")

        assert_in_outputted_to_buffer("1 + 2;", "3.0")
        assert_in_outputted_to_buffer("1 - 1;", "0.0")
        assert_in_outputted_to_buffer("1 * 0;", "0.0")
        assert_in_outputted_to_buffer("14 * 2;", "28.0")
        assert_in_outputted_to_buffer("14 * 2;", "28.0")
        assert_in_outputted_to_buffer("1.25 * 2;", "2.5")
        assert_in_outputted_to_buffer("7/7.0;", "1.0")
        assert_in_outputted_to_buffer("5/2;", "2.5")

    def test_divide_by_zero(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        tokens = lexer.scan("1/0;")
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        with pytest.raises(InterpreterRuntimeError, match="Cannot divide by zero."):
            interpreter.interpret(statements)

    def test_grouping(self) -> None:
        assert_in_outputted_to_buffer("(1);", "1")
        assert_in_outputted_to_buffer("(1 + 1);", "2.0")
        assert_in_outputted_to_buffer("(1 + 1 + 1);", "3.0")
        assert_in_outputted_to_buffer(
            "(1) + (1 + 1) + (1 + 1 + 1) + (1 + 1 + 1 + 1);", "10.0"
        )

    def test_numeric_expressions(self) -> None:
        assert_in_outputted_to_buffer("2 * (42 + 5);", "94.0")
        assert_in_outputted_to_buffer("(4 + 17 - 3)/(14/2);", "2.5714285714285716")
        assert_in_outputted_to_buffer("((1043 + 9) - (304 * 2))/(9 + 8 - 2);", "29.6")

    def test_print_statement(self) -> None:
        assert_in_outputted_to_buffer('print "hello world";', "\ue285 hello world")

    def test_history_statement(self) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = UnitTestMock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        # stage items in the history buffer.
        terminal_buffer._remember(
            [TerminalBufferUserInput("hello world"), TerminalBufferUserInput("1.42")]
        )

        # Run the 'history' statement;
        tokens = lexer.scan("history;")
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)

        output_msgs: List[str] = list(
            map(lambda l: l.raw_content(), terminal_buffer.output())
        )

        # Assert that running the 'history' statement copied the contents
        # of the history buffer into the scroll back buffer.
        assert "hello world" in output_msgs
        assert "1.42" in output_msgs

    def test_variable_declaration(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        tokens = lexer.scan("var a = 1;")
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()

        a_token: Token = Token(TokenType.IDENTIFIER, lexeme="a", literal=None, line=0)
        assert not (a_token.lexeme in interpreter._scoped_environment._in_memory_values)
        interpreter.interpret(statements)
        assert a_token.lexeme in interpreter._scoped_environment._in_memory_values
        assert interpreter._scoped_environment.get(a_token) == 1

    def test_assignment(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        # Do the initial declaration.
        tokens = lexer.scan("var x = 14.2;")
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)
        x_token: Token = Token(TokenType.IDENTIFIER, lexeme="x", literal=None, line=0)
        assert x_token.lexeme in interpreter._scoped_environment._in_memory_values
        assert interpreter._scoped_environment.get(x_token) == 14.2

        # Test reassigning the existing variable.
        tokens = lexer.scan("x = 42.7;")
        parser = Parser(tokens)
        statements = parser.parse()
        interpreter.interpret(statements)
        assert interpreter._scoped_environment.get(x_token) == 42.7

    def test_simple_block(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        # Do the initial declaration.
        code = """
    var x = 2;
    {
      var x = False;
      print x;
    }
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)

        assert 2 == interpreter._scoped_environment._in_memory_values["x"]

    def test_while_loop(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        # Do the initial declaration.
        code: str = """
    var i = 0;
    while (i < 10){
      print i;
      i = i + 1;
    }
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)
        assert 10 == interpreter._scoped_environment._in_memory_values["i"]

    def test_classic_for_loop(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)
        resolver = Resolver(interpreter)

        # Do the initial declaration.
        code: str = """
    var log = 0;
    for (var i = 0; i < 10; i = i + 1){
      log = i;
    }
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        resolver.resolve(statements)
        interpreter.interpret(statements)
        assert 9 == interpreter._scoped_environment._in_memory_values["log"]
        assert "i" not in interpreter._scoped_environment._in_memory_values

    def test_for_loop_with_no_initializer(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        # Do the initial declaration.
        code: str = """
    var i = 0;
    for (; i < 10; i = i + 1){
      True;
    }
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)
        assert 10 == interpreter._scoped_environment._in_memory_values["i"]

    def test_for_loop_with_no_increment(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        # Do the initial declaration.
        code: str = """
    var i = 0;
    for (; i < 10; ){
      i = i + 1;
    }
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)
        assert 10 == interpreter._scoped_environment._in_memory_values["i"]

    def test_unhandled_break_stmt(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        code = """
    break;
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()

        with pytest.raises(
            InterpreterRuntimeError, match="A control flow signal was not handled."
        ):
            interpreter.interpret(statements)

    def test_break_stmt(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        code = """
    var i = 0;
    while (i < 100){
      if (i == 5){
        break;
      }
      i = i + 1;
    }
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)
        assert 5 == interpreter._scoped_environment._in_memory_values["i"]

    def test_unhandled_continue_stmt(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        code = """
    continue;
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()

        with pytest.raises(
            InterpreterRuntimeError, match="A control flow signal was not handled."
        ):
            interpreter.interpret(statements)

    def test_modulo(self, mocker: MockFixture) -> None:
        """
        Given:
          dividend/divisor = quotient with remainder

        Modulo
          dividend % divisor = dividend - (round_down(dividend / divisor) * divisor)
        """
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        code = """
    var a = 0 % 1;
    var b = 2 % 1; 
    var c = 2 % 2; 
    var d = 3 % 2; 
    var e = 13 % 2; 
    var g = 13 % 5; 
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)
        assert 0 == interpreter._scoped_environment._in_memory_values["a"]
        assert 0 == interpreter._scoped_environment._in_memory_values["b"]
        assert 0 == interpreter._scoped_environment._in_memory_values["c"]
        assert 1 == interpreter._scoped_environment._in_memory_values["d"]
        assert 1 == interpreter._scoped_environment._in_memory_values["e"]
        assert 3 == interpreter._scoped_environment._in_memory_values["g"]

    def test_continue_stmt(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        code = """
    var i = 0;
    var x = 0;
    while (i < 10){
      i = i + 1;
      if (i % 2 == 0){
        continue;
      }
      x = x + 1;
    }
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)
        assert 10 == interpreter._scoped_environment._in_memory_values["i"]
        assert 5 == interpreter._scoped_environment._in_memory_values["x"]

    def test_concatenate_strings(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)

        code = """
    var msg = 'abc'+'def' +'hij';
    var another_msg = 'abc' + 123;
    var a_num = 123 + 456;
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        interpreter.interpret(statements)
        assert "abcdefhij" == interpreter._scoped_environment._in_memory_values["msg"]
        assert (
            "abc123" == interpreter._scoped_environment._in_memory_values["another_msg"]
        )
        assert 579 == interpreter._scoped_environment._in_memory_values["a_num"]

    def test_func_declarations(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)
        resolver = Resolver(interpreter)

        code = """
    func add(a,b){
      return a + b;
    }

    var sum = add(11.2, 1);
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        resolver.resolve(statements)
        interpreter.interpret(statements)
        assert "add" in interpreter._scoped_environment._in_memory_values
        assert 12.2 == interpreter._scoped_environment._in_memory_values["sum"]

    def test_closure_support(self, mocker: MockFixture) -> None:
        lexer = Lexer()
        terminal_buffer = TerminalBuffer()
        terminal_display = mocker.Mock()
        interpreter = TerminalInterpreter(terminal_buffer, terminal_display)
        resolver = Resolver(interpreter)

        code = """
    func make_counter(){
      var count = 0;
      func counter(){
        count = count + 1;
        return count;
      }
      return counter;
    }

    var counter = make_counter();
    var first_call = counter();
    var second_call = counter();
    var third_call = counter();
    """
        tokens = lexer.scan(code)
        parser = Parser(tokens)
        statements: List[Stmt] = parser.parse()
        resolver.resolve(statements)
        interpreter.interpret(statements)
        assert 1 == interpreter._scoped_environment._in_memory_values["first_call"]
        assert 2 == interpreter._scoped_environment._in_memory_values["second_call"]
        assert 3 == interpreter._scoped_environment._in_memory_values["third_call"]
