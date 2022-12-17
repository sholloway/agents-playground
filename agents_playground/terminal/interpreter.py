
from enum import Enum, auto
from numbers import Number
from typing import Any, List, cast

from agents_playground.terminal.ast.statements import ( 
  Block,
  Break,
  Clear,
  Expression,
  History,
  If,
  Print,
  Stmt, 
  StmtVisitor,
  Var,
  While 
)
from agents_playground.terminal.ast.expressions import ( 
  Assign,
  Expr,
  BinaryExpr,
  ExprVisitor, 
  GroupingExpr, 
  LiteralExpr,
  LogicalExpr, 
  UnaryExpr,
  Variable
)
from agents_playground.terminal.environment import Environment
from agents_playground.terminal.interpreter_runtime_error import BreakStatementSignal, ControlFlowSignal, InterpreterRuntimeError
from agents_playground.terminal.terminal_buffer import TerminalBuffer, TerminalBufferUnformattedText
from agents_playground.terminal.terminal_display import TerminalDisplay
from agents_playground.terminal.token import Token
from agents_playground.terminal.token_type import TokenType

class InterpreterMode(Enum):
  COMMAND = auto()
  INSERT  = auto()

class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
  def __init__(self, buffer: TerminalBuffer, display: TerminalDisplay) -> None:
    super().__init__()
    self._terminal_buffer = buffer
    self._terminal_display = display
    self._environment: Environment = Environment()
    self._interpreter_mode:InterpreterMode; #Assigned during interpret() invocation

  def interpret(self, statements: List[Stmt], mode: InterpreterMode = InterpreterMode.COMMAND) -> None:
    self._interpreter_mode = mode
    try:
      for statement in statements:
        self._execute(statement)
    except ControlFlowSignal as cf:
      raise InterpreterRuntimeError(cf.token, 'A control flow signal was not handled.') from cf

  def _execute(self, stmt: Stmt):
    stmt.accept(self)

  def _evaluate(self, expression: Expr) -> Any:
    return expression.accept(self)
  
  def visit_var_declaration(self, decl: Var) -> None:
    """Handle visiting a variable declaration statement."""
    # If the declaration isn't initialized, initialize it. 
    # Either way then store it in the environment.
    # This is done to support both use cases:
    # 1. let x;
    # 2. let x = 5;
    value: Any | None = None
    if decl.initializer:
      value = self._evaluate(decl.initializer)
    self._environment.define(decl.name.lexeme, value)
    return

  def visit_block_stmt(self, block: Block) -> None:
    """Handle visiting a block of statements."""
    self._execute_block(block.statements, Environment(self._environment))

  def visit_assign_expr(self, expression: Assign) -> Any:
    value: Any = self._evaluate(expression.value)
    self._environment.assign(expression.name, value)
    return value

  def visit_expression_stmt(self, stmt: Expression) -> None:
    """Handle visiting an expression statement."""
    result: Any = self._evaluate(stmt.expression)
    if self._interpreter_mode == InterpreterMode.COMMAND:
      self._terminal_buffer.append_output(TerminalBufferUnformattedText(f'{str(result)}'), remember=False)
      self._terminal_display.refresh(self._terminal_buffer)

  def visit_if_statement(self, if_stmt: If) -> None:
    """Handle visiting an if statement."""
    if self._truth_value(self._evaluate(if_stmt.condition)):
      self._execute(if_stmt.then_branch)
    elif if_stmt.else_branch is not None:
      self._execute(if_stmt.else_branch)
    return None

  def visit_while_statement(self, while_stmt: While) -> None:
    """Handle visiting a while statement."""
    while self._truth_value(self._evaluate(while_stmt.condition)):
      try:
        self._execute(while_stmt.body)
      except BreakStatementSignal:
        break;
    return None

  def visit_break_stmt(self, breakStmt: Break) -> None:
    """Handle visiting a break statement."""
    raise BreakStatementSignal(breakStmt.token)
  
  def visit_print_stmt(self, stmt: Print) -> None:
    """Handle visiting a print statement."""
    value: Any = self._evaluate(stmt.expression)
    self._terminal_buffer.append_output(TerminalBufferUnformattedText(f'{chr(0xE285)} {str(value)}'), remember=False)
    self._terminal_display.refresh(self._terminal_buffer)

  def visit_clear_stmt(self, stmt: Clear) -> None:
    """Handle visiting a 'clear' statement."""
    self._terminal_buffer.clear()
    self._terminal_display.refresh(self._terminal_buffer)
    return
  
  def visit_history_stmt(self, stmt: History) -> None:
    self._terminal_buffer.append_output(
      self._terminal_buffer.history(), 
      remember=False
    )
    self._terminal_display.refresh(self._terminal_buffer)

  def _execute_block(self, statements: List[Stmt], local_environment: Environment):
    previous_env: Environment = self._environment
    try:
      self._environment = local_environment
      statement: Stmt
      for statement in statements:
        self._execute(statement)
    finally:
      self._environment = previous_env

  def _truth_value(self, value: Any) -> bool:
    """Returns the truth value (True/False) of an expression.
    
    The truth rules are:
    1. None -> False
    2. Boolean values return their value.
    3. 0 | 0.0 -> False
    4. 1 | 1.0 -> True
    3. Anything that is assigned (e.g. x = 'abc') returns true.
    """
    match value:
      case None:
        return False
      case bool(_):
        return value
      case 0 | 0.0:
        return False
      case 1 | 1.0:
        return True
      case _:
        return True

  def _is_equal(self, left: Any, right: Any) -> bool:
    """Determine if two values are equal."""
    # Note: Using the same equality rules as Python.
    left_eq_to_right = left.__eq__(right)
    if isinstance(left_eq_to_right, bool):
      return left_eq_to_right
    else:
      right_eq_to_left = right.__eq__(left)
      if isinstance(right_eq_to_left, bool):
        return right_eq_to_left
      else:
        return False

  def _check_number_operand(self, operator: Token, operand: Any) -> None:
    if isinstance(operand, Number):
      return
    else:
      raise InterpreterRuntimeError(operator, 'Operand must be a number.')
  
  def _check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
    if isinstance(left, Number) and isinstance(right, Number):
      return
    else:
      raise InterpreterRuntimeError(operator, 'Operands must both be numbers.')
    
  def _enforce_no_divide_by_zero(self, operator: Token, possible_number: Any) -> None:
    if isinstance(possible_number, Number) and possible_number == 0:
      raise InterpreterRuntimeError(operator, 'Cannot divide by zero.')

  def visit_binary_expr(self, expression: BinaryExpr) -> Any:
    """Handle visiting a binary expression."""
    # 1. First evaluate the left side of the expression and then the right side.
    left:  Any = self._evaluate(expression.left)
    right: Any = self._evaluate(expression.right)

    # 2. Evaluate the binary operand by applying it to the results of the left and right.
    match expression.operator.type:
      case TokenType.MINUS:
        self._check_number_operands(expression.operator, left, right)
        return float(left) - float(right)
      case TokenType.PLUS: # Plus can both add numbers and concatenate strings.
        if isinstance(left, Number) and isinstance(right, Number):
          # Handle adding two numbers.
          # Note: The values True/False will be converted to 1/0.
          return float(cast(float, left)) + float(cast(float, right))
        elif  (isinstance(left, str)    or isinstance(right, str)) and \
              (isinstance(left, Number) or isinstance(right, Number)):
          # If either the left or right is a string create a new string by joining the values.
          return str(left) + str(right)
        else:
          raise InterpreterRuntimeError(expression.operator, 'Operands must be a combination of numbers and strings.')
      case TokenType.SLASH:
        self._check_number_operands(expression.operator, left, right)
        self._enforce_no_divide_by_zero(expression.operator, right)
        return float(left)/float(right)
      case TokenType.STAR:
        self._check_number_operands(expression.operator, left, right)
        return float(left) * float(right)
      case TokenType.GREATER:
        self._check_number_operands(expression.operator, left, right)
        return left > right
      case TokenType.GREATER_EQUAL:
        self._check_number_operands(expression.operator, left, right)
        return left >= right
      case TokenType.LESS:
        self._check_number_operands(expression.operator, left, right)
        return left < right
      case TokenType.LESS_EQUAL:
        self._check_number_operands(expression.operator, left, right)
        return left <= right
      case TokenType.BANG_EQUAL:
        return not self._is_equal(left,right)
      case TokenType.EQUAL_EQUAL:
        return self._is_equal(left,right)
      case _:
        # shouldn't get here.
        # TODO: Throw an error.
        return None
  
  def visit_grouping_expr(self, expression: GroupingExpr) -> Any:
    """Handle visiting a grouping expression."""
    return self._evaluate(expression.expression)
  
  def visit_literal_expr(self, expression: LiteralExpr) -> Any:
    """Handle visiting a literal expression."""
    return expression.value

  def visit_logical_expr(self, expression: LogicalExpr) -> Any:
    """Handle visiting a logical expression."""
    left: Any = self._evaluate(expression.left)
    if expression.operator.type == TokenType.OR:
      if self._truth_value(left):
        return left 
    else:
      if not self._truth_value(left):
        return left

    # If the operation is not OR and the left IS truthy then evaluate the right. 
    return self._evaluate(expression.right)
  
  def visit_unary_expr(self, expression: UnaryExpr) -> Any:
    """Handle visiting a unary expression."""
    # 1. First evaluate the right side of the expression
    right: Any  = self._evaluate(expression.right)

    # 2. Evaluate the unary operator.
    match expression.operator.type:
      case TokenType.BANG:
        return not self._truth_value(right)
      case TokenType.MINUS:
        self._check_number_operand(expression.operator, right)
        return -float(right)

    # This should be unreachable.
    # TODO: Throw an error rather than return None.
    return None
  
  def visit_variable_expr(self, expression: Variable) -> Any:
    """Handle visiting a variable."""
    return self._environment.get(expression.name)