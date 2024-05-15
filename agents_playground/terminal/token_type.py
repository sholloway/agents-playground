from enum import Enum, auto


class TokenType(Enum):
    # Single character tokens.
    LEFT_BRACE = auto()  # {
    RIGHT_BRACE = auto()  # }
    LEFT_PAREN = auto()  # (
    RIGHT_PAREN = auto()  # )
    COMMA = auto()  # ,
    DOT = auto()  # .
    MINUS = auto()  # -
    PLUS = auto()  # +
    STAR = auto()  # *
    SLASH = auto()  # /
    BACKSLASH = auto()  # \
    MOD = auto()  # %

    # One or two character tokens.
    BANG = auto()  #!
    BANG_EQUAL = auto()  # !=
    EQUAL = auto()  # =
    EQUAL_EQUAL = auto()  # ==
    GREATER = auto()  # >
    GREATER_EQUAL = auto()  # >=
    LESS = auto()  # <
    LESS_EQUAL = auto()  # <=

    # Literals
    IDENTIFIER = auto()
    STRING = auto()  # could be via '...' or "..."
    NUMBER = auto()  # Integers and floating point
    TRUE = auto()
    FALSE = auto()
    NONE = auto()

    # Internal
    SEMICOLON = auto()  # ; is used to indicate the end of a statement.
    EOF = auto()  # End of the source string/file.

    # Keywords
    VAR = auto()  # Variable declaration.
    FUNC = auto()  # Function declaration.
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    AND = auto()
    OR = auto()
    WHILE = auto()
    FOR = auto()
    BREAK = auto()
    CONTINUE = auto()
    CLEAR = auto()
    PRINT = auto()
    HISTORY = auto()
