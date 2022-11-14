
from agents_playground.terminal.ast import BinaryExpr, GroupingExpr, InlineASTFormatter, LiteralExpr, UnaryExpr
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
  def test_parse_some_stuff(self) -> None:
    pass

