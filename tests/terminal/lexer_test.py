
from typing import List
from agents_playground.terminal.lexer import Lexer, Token, TokenType

def assert_token(token, type, lexeme, literal, line) -> None:
  assert token.type == type, f'Wrong token type found. Expected {type} had {token.type}'
  assert token.lexeme == lexeme, f'Wrong token lexeme found. Expected {lexeme} had {token.lexeme}'
  assert token.literal == literal, f'Wrong token literal found. Expected {literal} had {token.literal}'
  assert token.line == line, f'Wrong token line found. Expected {line} had {token.line}'

class TestLexer:
  def test_scan_single_tokens(self) -> None:
    lexer = Lexer()
    tokens: List[Token] = lexer.scan('(),.-+*')
    
    assert len(tokens) == 8, 'Expected 8 tokens scanned. 7 + EOF'
    assert_token(tokens[0], TokenType.LEFT_PAREN,   '(', None, 0)    
    assert_token(tokens[1], TokenType.RIGHT_PAREN,  ')', None, 0)    
    assert_token(tokens[2], TokenType.COMMA,        ',', None, 0)    
    assert_token(tokens[3], TokenType.DOT,          '.', None, 0)    
    assert_token(tokens[4], TokenType.MINUS,        '-', None, 0)    
    assert_token(tokens[5], TokenType.PLUS,         '+', None, 0)    
    assert_token(tokens[6], TokenType.STAR,         '*', None, 0)    
    assert_token(tokens[7], TokenType.EOF,          '',  None, 0)    
