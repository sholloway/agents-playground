"""
A module that handles scanning the input of the console and converts it into 
a list of tokens.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, List


class TokenType(Enum):
  # Single character tokens.
  LEFT_PAREN = auto() # (
  RIGHT_PAREN = auto() # )
  COMMA = auto() # ,
  DOT = auto() # .
  MINUS = auto() # -
  PLUS = auto() # +
  STAR = auto() # *
  SLASH = auto() # /
  BACKSLASH = auto() # \

  # One or two character tokens.
  BANG = auto() #!
  BANG_EQUAL = auto() # !=
  EQUAL_EQUAL = auto # ==
  GREATER = auto() # > 
  GREATER_EQUAL = auto () # >=
  LESS = auto() # <
  LESS_EQUAL = auto() # <=
  
  # Literals
  IDENTIFIER = auto() 
  STRING = auto() # could be via '...' or "..."
  NUMBER = auto() # Integers and floating point
  
  # Keywords
    # TBD

@dataclass
class Token:
  type: TokenType
  lexeme: str
  literal: Any 
  line: int

"""
Commands
- tty
- clear
- ls (?)
- help <cmd>
- commands
"""


"""
What are the scanning use cases?
- Single Token Use cases
- Lexical errors
- Operators
- Division
- New lines, tabs, spaces
- String literals
- Number literals
- Reserved words
"""
class Lexer:
  def __init__(self) -> None:
    pass

  def scan(input_code: str) -> List[Token]:
    tokens: List[Token] = []
    return tokens
