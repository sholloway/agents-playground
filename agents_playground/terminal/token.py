from dataclasses import dataclass
from typing import Any

from agents_playground.terminal.token_type import TokenType

@dataclass
class Token:
  type: TokenType
  lexeme: str
  literal: Any 
  line: int