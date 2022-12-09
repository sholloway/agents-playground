from agents_playground.terminal.ast.expressions import Assign, BinaryExpr, Expr, ExprVisitor, GroupingExpr, LiteralExpr, UnaryExpr, Variable

class InlineASTFormatter(ExprVisitor[str]):
  def _parenthesize(self, name: str, *expressions: Expr) -> str:
    result = f'({name}'

    for expr in expressions:
      result += ' '
      result += expr.accept(self)
    
    result += ')'
    return result

  """Given the root of an AST, formats a string suitable for printing."""
  def format(self, expression: Expr) -> str:
    return expression.accept(self)

  def visit_binary_expr(self, expression: BinaryExpr) -> str:
    """Handle visiting a binary expression."""
    return self._parenthesize(expression.operator.lexeme, expression.left, expression.right)
  
  def visit_grouping_expr(self, expression: GroupingExpr) -> str:
    """Handle visiting a grouping expression."""
    return self._parenthesize('group', expression.expression)
  
  def visit_literal_expr(self, expression: LiteralExpr) -> str:
    """Handle visiting a literal expression."""
    if expression.value is None:
      return 'None'
    return str(expression.value)
  
  def visit_unary_expr(self, expression: UnaryExpr) -> str:
    """Handle visiting a unary expression."""
    return self._parenthesize(expression.operator.lexeme, expression.right)

  def visit_variable_expr(self, expression: Variable) -> str:
    """Handle visiting a variable."""
    return '' # TODO: Implement this.

  def visit_assign_expr(self, expression: Assign) -> str:
    """Handle visiting an assignment."""
    return '' # TODO: Implement this.