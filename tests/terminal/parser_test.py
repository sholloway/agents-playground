
from typing import List
from agents_playground.terminal.ast import BinaryExpr, Expr, GroupingExpr, InlineASTFormatter, LiteralExpr, UnaryExpr
from agents_playground.terminal.lexer import Lexer
from agents_playground.terminal.parser import Parser
from agents_playground.terminal.token import Token
from agents_playground.terminal.token_type import TokenType

class TestASTFormatter:
  def test_simple_expr(self) -> None:
    expression = BinaryExpr(
      UnaryExpr(
        Token(TokenType.MINUS, '-', None, 1),
        LiteralExpr(123)
      ),
      Token(TokenType.STAR, '*', None, 1),
      GroupingExpr(LiteralExpr(45.67))
    )

    formatted_ast = InlineASTFormatter().format(expression)
    assert '(* (- 123) (group 45.67))' == formatted_ast, 'Error formatting an AST.'

class TestParser:
  def test_parse_single_number(self) -> None:
    lexer = Lexer()
    tokens = lexer.scan('1978')
    parser = Parser(tokens)
    expr: Expr = parser.parse()
    assert not parser._encountered_error
    formatted_ast = InlineASTFormatter().format(expr)
    assert '1978' == formatted_ast


  def test_parse_string(self) -> None:
    lexer = Lexer()
    tokens = lexer.scan('"abcdefg"')
    parser = Parser(tokens)
    expr: Expr = parser.parse()
    assert not parser._encountered_error
    formatted_ast = InlineASTFormatter().format(expr)
    assert 'abcdefg' == formatted_ast
  
  def test_parse_booleans(self) -> None:
    lexer = Lexer()
    tokens: List[Token] = lexer.scan('True')
    parser = Parser(tokens)
    expr: Expr = parser.parse()
    assert not parser._encountered_error
    formatted_ast = InlineASTFormatter().format(expr)
    assert 'True' == formatted_ast
    
    tokens = lexer.scan('False')
    parser = Parser(tokens)
    expr = parser.parse()
    assert not parser._encountered_error
    formatted_ast = InlineASTFormatter().format(expr)
    assert 'False' == formatted_ast
    
    tokens = lexer.scan('True == False')
    parser = Parser(tokens)
    expr = parser.parse()
    assert not parser._encountered_error
    formatted_ast = InlineASTFormatter().format(expr)
    assert '(== True False)' == formatted_ast

  def test_parse_arithmetic(self) -> None:
    lexer = Lexer()
    tokens: List[Token] = lexer.scan('1 + 2 * 3 / 4')
    parser = Parser(tokens)
    expr: Expr = parser.parse()
    assert not parser._encountered_error
    formatted_ast = InlineASTFormatter().format(expr)
    assert '(+ 1 (/ (* 2 3) 4))' == formatted_ast
