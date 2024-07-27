"""
A recursive descent parser for the Agent Terminal language.
"""

from typing import Callable, List
from agents_playground.legacy.terminal.ast.statements import (
    Block,
    Break,
    Continue,
    Expression,
    Function,
    If,
    Return,
    Stmt,
    Clear,
    History,
    Print,
    Var,
    While,
)
from agents_playground.legacy.terminal.ast.expressions import (
    Assign,
    Call,
    Expr,
    BinaryExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    Variable,
)
from agents_playground.legacy.terminal.constants import TERM_MAX_ARG_SIZE
from agents_playground.legacy.terminal.token import Token
from agents_playground.legacy.terminal.token_type import TokenType


class ParseError(Exception):
    def __init__(self, token: Token, error_msg: str) -> None:
        super().__init__(error_msg)
        self._token = token

    @property
    def token(self) -> Token:
        return self._token


def default_error_handler(line: int, messages: List[str]) -> None:
    print(f"Error on line {line}")
    for msg in messages:
        print(msg)


class Parser:
    """A recursive descent parser for the Terminal Language.
    Each statement in the grammar maps to a function on the parser.
    """

    def __init__(
        self,
        tokens: List[Token],
        error_handler: Callable[[int, List[str]], None] = default_error_handler,
    ) -> None:
        self._tokens = tokens
        self._current = 0
        self._encountered_error = False
        self._error_handler = error_handler
        self._statement_map = {
            TokenType.IF: self._if_statement,
            TokenType.WHILE: self._while_statement,
            TokenType.FOR: self._for_statement,
            TokenType.BREAK: self._break_statement,
            TokenType.CONTINUE: self._continue_statement,
            TokenType.LEFT_BRACE: self._left_brace,
            TokenType.RETURN: self._return_statement,
            TokenType.PRINT: self._print_statement,
            TokenType.CLEAR: self._clear_statement,
            TokenType.HISTORY: self._history_statement,
        }

    def parse(self) -> List[Stmt]:
        """
        Implements Grammar Rule
        program -> declaration* EOF ;
        """
        statements: List[Stmt] = []
        current_statement: Stmt | None = None
        while not self._is_at_end():
            current_statement = self._declaration()
            if current_statement is not None:
                statements.append(current_statement)
        return statements

    def _declaration(self) -> Stmt | None:
        """
        Implements Grammar Rule
        declaration -> funDecl | varDecl | statement ;
        """
        try:
            if self._match(TokenType.FUNC):
                return self._function("function")
            elif self._match(TokenType.VAR):
                return self._var_declaration()
            else:
                return self._statement()
        except ParseError as pe:
            self._synchronize()
            return None

    def _function(self, kind: str) -> Function:
        # 1. Consume the name of the function declaration.
        name: Token = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")

        # 2. Consume the opening ( of the function declaration.
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        # 3. Process all of the parameters.
        parameters: List[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= TERM_MAX_ARG_SIZE:
                    self._error(
                        self._peek(),
                        f"Cannot have more than {TERM_MAX_ARG_SIZE} parameters.",
                    )
                parameters.append(
                    self._consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self._match(TokenType.COMMA):
                    break

        # 4. Consume the closing ).
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        # 5. Parse the body of the function declaration.
        self._consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body: List[Stmt] = self._block()
        return Function(name, parameters, body)

    def _synchronize(self) -> None:
        """When an error has occurred parsing, jump forward until the next viable token is discovered."""
        self._advance()
        while not self._is_at_end():
            if self._previous() == TokenType.SEMICOLON:
                return None

        next_token: Token = self._peek()

        match next_token.type:
            case TokenType.VAR | TokenType.PRINT | TokenType.CLEAR | TokenType.HISTORY:
                return None

        self._advance()
        return None

    def _var_declaration(self) -> Stmt:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expected variable name.")
        initializer: Expr | None = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _expression(self) -> Expr:
        """
        Implements Grammar Rule
        expression -> assignment;
        """
        return self._assignment()

    def _assignment(self) -> Expr:
        """
        Implements Grammar Rule
        assignment  -> IDENTIFIER "=" assignment | logic_or ;
        """
        expr: Expr = self._or()
        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expr = self._assignment()  # recursively parse the right-hand side.

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)
            else:
                """
                Report an error, but don't raise it because the parser isn't
                in a confused state that requires going into panic mode
                and synchronizing.
                """
                self._error(equals, "Invalid assignment target.")
        return expr

    def _or(self) -> Expr:
        """
        Implements Grammar Rule
        logic_or -> logic_and ( "or" logic_and )*;
        """
        expr: Expr = self._and()
        while self._match(TokenType.OR):
            operator: Token = self._previous()
            right: Expr = self._and()
            expr = LogicalExpr(expr, operator, right)
        return expr

    def _and(self) -> Expr:
        """
        Implements Grammar Rule
        logic_and   -> equality ( "and" equality )*;
        """
        expr: Expr = self._equality()
        while self._match(TokenType.AND):
            operator: Token = self._previous()
            right: Expr = self._equality()
            expr = LogicalExpr(expr, operator, right)
        return expr

    def _statement(self) -> Stmt:
        """
        Implements Grammar Rule
        statement ->  exprStmt   |
                        ifStmt     |
                        blockStmt  |
                        whileStmt  | forStmt      |
                        returnStmt |
                        breakStmt  | continueStmt |
                        printStmt  | clearStmt    | historyStmt;
        """
        for token_type in self._statement_map:
            if self._match(token_type):
                return self._statement_map[token_type]()
        return self._expression_statement()

    def _left_brace(self) -> Stmt:
        return Block(self._block())

    def _return_statement(self) -> Stmt:
        """
        Implements Grammar Rule
        returnStmt -> "return" expression? ";" ;
        """
        keyword: Token = self._previous()
        value: Expr | None = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def _if_statement(self) -> Stmt:
        """
        Implements Grammar Rule
        ifStmt  -> "if" "(" expression ")" statement
                    ( "else" statement )? ;
        """
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt = self._statement()
        else_branch: Stmt | None = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        return If(condition, then_branch, else_branch)

    def _while_statement(self) -> Stmt:
        """
        Implements Grammar Rule
        whileStmt -> "while" "(" expression ")" statement;
        """
        self._consume(TokenType.LEFT_PAREN, "Expect a '(' after 'while'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after 'while condition'.")
        body: Stmt = self._statement()
        return While(condition, body)

    def _for_statement(self) -> Stmt:
        """
        Implements Grammar Rule
        forStmt -> "for" "(" (varDecl | exprStmt | ";" )
                    expression? ";"
                    expression? ")" statement;
        """
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        # 1. Handle the initializer
        # "for" "(" (varDecl | exprStmt | ";" )
        initializer: Stmt | None = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        # 2. Handle the loop condition
        # expression? ";"

        condition: Expr | None = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        # 3. Handle the incrementor.
        # expression? ")"
        increment: Expr | None = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        # 4. Handle the body of the for loop.
        # statement;
        body: Stmt = self._statement()

        # Desugar the for loop into a while loop.
        # http://craftinginterpreters.com/control-flow.html#desugaring
        # This will build a block of the form:
        # {
        #   initializer;
        #   while(condition){
        #     block;
        #     increment;
        #   }
        # }
        if increment is not None:
            # Note: The increment, if there is one, executes after the body.
            body = Block([body, Expression(increment)])

        if condition is None:
            condition = LiteralExpr(True)

        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def _block(self) -> List[Stmt]:
        """
        Implements Grammar Rule
        blockStmt -> "{" declaration* "}" ;
        """
        statements: List[Stmt] = []
        current_statement: Stmt | None
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            current_statement = self._declaration()
            if current_statement is not None:
                statements.append(current_statement)
        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after code block.")
        return statements

    def _expression_statement(self) -> Stmt:
        value: Expr = self._expression()
        self._consume(
            TokenType.SEMICOLON, "A ';' is required at the end of a statement."
        )
        return Expression(value)

    def _break_statement(self) -> Stmt:
        last_token: Token = (
            self._previous()
        )  # grab the last token for error handling...
        self._consume(
            TokenType.SEMICOLON, "A ';' is required at the end of a break statement."
        )
        return Break(last_token)

    def _continue_statement(self) -> Stmt:
        last_token: Token = (
            self._previous()
        )  # grab the last token for error handling...
        self._consume(
            TokenType.SEMICOLON, "A ';' is required at the end of a continue statement."
        )
        return Continue(last_token)

    def _print_statement(self) -> Stmt:
        value: Expr = self._expression()
        self._consume(
            TokenType.SEMICOLON, "A ';' is required at the end of a print statement."
        )
        return Print(value)

    def _clear_statement(self) -> Stmt:
        self._consume(
            TokenType.SEMICOLON, "A ';' is required at the end of a clear statement."
        )
        return Clear()

    def _history_statement(self) -> Stmt:
        self._consume(
            TokenType.SEMICOLON, "A ';' is required at the end of a history statement."
        )
        return History()

    def _equality(self) -> Expr:
        """
        Implements Grammar Rule
            equality -> comparison ( ( "!=" | "==" ) comparison )*;
        """
        expr: Expr = self._comparison()
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self._previous()
            right: Expr = self._comparison()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def _match(self, *types: TokenType) -> bool:
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False

    def _check(self, type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _is_at_end(self):
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _previous(self) -> Token:
        return self._tokens[self._current - 1]

    def _comparison(self) -> Expr:
        """
        Implements Grammar Rule
        comparison -> term ( (">" | ">=" | "<" | "<=") term )*;
        """
        expr: Expr = self._term()
        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator: Token = self._previous()
            right: Expr = self._term()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def _term(self) -> Expr:
        """
        Implements Grammar Rule
        term -> factor ( ( "-" | "+") unary )*;
        """
        expr: Expr = self._factor()
        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self._previous()
            right: Expr = self._factor()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def _factor(self) -> Expr:
        """
        Implements Grammar Rule
        factor -> unary ( ( "/" | "*" | "%") unary )*;
        """
        expr: Expr = self._unary()
        while self._match(TokenType.SLASH, TokenType.STAR, TokenType.MOD):
            operator: Token = self._previous()
            right: Expr = self._unary()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def _unary(self) -> Expr:
        """
        Implements Grammar Rule
        unary -> ( "!" | "-" ) unary | call ;
        """
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self._previous()
            right: Expr = self._unary()
            return UnaryExpr(operator, right)
        return self._call()

    def _call(self) -> Expr:
        """
        Implements Grammar Rule
        call -> primary ( "(" arguments? ")" )* ;
        """
        expr: Expr = self._primary()
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            else:
                break
        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: List[Expr] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= TERM_MAX_ARG_SIZE:
                    self._error(
                        self._peek(),
                        f"Cannot have more than {TERM_MAX_ARG_SIZE} TERM_MAX_ARG_SIZE.",
                    )
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        paren: Token = self._consume(
            TokenType.RIGHT_PAREN, "Expect ')' after arguments."
        )
        return Call(callee, paren, arguments)

    def _primary(self) -> Expr:
        """
        Implements Grammar Rule
        primary ->  NUMBER |
                    STRING |
                    "true" | "false" |
                    "None" |
                    "(" expression ")" |
                    IDENTIFIER;
        """
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        elif self._match(TokenType.TRUE):  # I'm expecting to hit here.
            return LiteralExpr(True)
        elif self._match(TokenType.NONE):
            return LiteralExpr(None)
        elif self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self._previous().literal)
        elif self._match(TokenType.LEFT_PAREN):
            expr: Expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, f"Expect ) after expression.")
            return GroupingExpr(expr)
        elif self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())
        else:
            raise self._error(self._peek(), "Expect expression.")

    def _consume(self, type: TokenType, error_msg: str) -> Token:
        if self._check(type):
            return self._advance()
        else:
            raise self._error(self._peek(), error_msg)

    def _error(self, token: Token, error_msg: str) -> ParseError:
        self._handle_error(token, error_msg)
        return ParseError(token, error_msg)

    def _handle_error(self, token: Token, error_msg: str) -> None:
        if token.type == TokenType.EOF:
            self._error_handler(token.line, ["At end", error_msg])
        else:
            self._error_handler(token.line, [f"At '{token.lexeme}'", error_msg])
