from enum import Enum, auto

class TokenType(Enum):
  # Single character tokens.
  LEFT_PAREN  = auto() # (
  RIGHT_PAREN = auto() # )
  COMMA       = auto() # ,
  DOT         = auto() # .
  MINUS       = auto() # -
  PLUS        = auto() # +
  STAR        = auto() # *
  SLASH       = auto() # /
  BACKSLASH   = auto() # \

  # One or two character tokens.
  BANG          = auto() #!
  BANG_EQUAL    = auto() # !=
  EQUAL         = auto() # =
  EQUAL_EQUAL   = auto() # ==
  GREATER       = auto() # > 
  GREATER_EQUAL = auto() # >=
  LESS          = auto() # <
  LESS_EQUAL    = auto() # <=
  
  # Literals
  IDENTIFIER  = auto() 
  STRING      = auto() # could be via '...' or "..."
  NUMBER      = auto() # Integers and floating point
  TRUE        = auto()
  FALSE       = auto()
  NONE        = auto()
  
  # Internal
  EOF = auto() #End of the source string/file.

  # Keywords
  CLEAR = auto()
  PRINT = auto()