from typing import List, cast
from agents_playground.legacy.terminal.ast.expressions import (
    BinaryExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
)
from agents_playground.legacy.terminal.ast.statements import (
    Expression,
    Stmt,
    StmtVisitor,
)
from agents_playground.legacy.terminal.lexer import Lexer
from agents_playground.legacy.terminal.parser import Parser
from agents_playground.legacy.terminal.token import Token
from agents_playground.legacy.terminal.token_type import TokenType


class TestParser:
    def test_parse_single_number(self) -> None:
        lexer = Lexer()
        tokens = lexer.scan("1978;")
        parser = Parser(tokens)
        ast: List[Stmt] = parser.parse()
        assert not parser._encountered_error
        assert len(ast) == 1
        assert isinstance(ast[0], Expression)
        assert isinstance(ast[0].expression, LiteralExpr)
        assert ast[0].expression.value == 1978

    def test_parse_string(self) -> None:
        lexer = Lexer()
        tokens = lexer.scan('"abcdefg";')
        parser = Parser(tokens)
        ast: List[Stmt] = parser.parse()
        assert not parser._encountered_error
        assert len(ast) == 1
        assert isinstance(ast[0], Expression)
        assert isinstance(ast[0].expression, LiteralExpr)
        assert ast[0].expression.value == "abcdefg"

    def test_parse_booleans(self) -> None:
        lexer = Lexer()
        tokens: List[Token] = lexer.scan("True;")
        parser = Parser(tokens)
        ast: List[Stmt] = parser.parse()
        assert not parser._encountered_error
        assert isinstance(ast[0].expression, LiteralExpr)
        assert ast[0].expression.value == True

        tokens = lexer.scan("False;")
        parser = Parser(tokens)
        ast = parser.parse()
        assert not parser._encountered_error
        assert isinstance(ast[0].expression, LiteralExpr)
        assert ast[0].expression.value == False

        tokens = lexer.scan("True == False;")
        parser = Parser(tokens)
        ast = parser.parse()
        assert not parser._encountered_error
        assert isinstance(ast[0], Expression)
        assert isinstance(ast[0].expression, BinaryExpr)
        assert isinstance(ast[0].expression.left, LiteralExpr)
        assert isinstance(ast[0].expression.right, LiteralExpr)
        assert isinstance(ast[0].expression.operator, Token)

        assert ast[0].expression.left.value == True
        assert ast[0].expression.right.value == False
        assert ast[0].expression.operator.type == TokenType.EQUAL_EQUAL

    """
  The below test should produce an AST of the form:
      +
    /   \
  1      /
        /  \
      *     4
    /   \
  2     3
  """

    def test_parse_arithmetic(self) -> None:
        lexer = Lexer()
        tokens: List[Token] = lexer.scan("1 + 2 * 3 / 4;")
        parser = Parser(tokens)
        ast: List[Stmt] = parser.parse()
        assert not parser._encountered_error
        assert len(ast) == 1
        assert isinstance(ast[0], Expression)
        assert isinstance(ast[0].expression, BinaryExpr)

        assert ast[0].expression.operator.type == TokenType.PLUS
        assert ast[0].expression.left.value == 1
        assert isinstance(ast[0].expression.right, BinaryExpr)

        assert ast[0].expression.right.operator.type == TokenType.SLASH
        assert isinstance(ast[0].expression.right.left, BinaryExpr)
        assert ast[0].expression.right.left.operator.type == TokenType.STAR
        assert ast[0].expression.right.right.value == 4
