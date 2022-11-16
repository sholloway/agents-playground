
from typing import List
from agents_playground.terminal.lexer import Lexer, Token, TokenType

def assert_token(token, type, lexeme, literal, line) -> None:
  assert token.type == type, f'Wrong token type found. Expected {type} had {token.type}'
  assert token.lexeme == lexeme, f'Wrong token lexeme found. Expected {lexeme} had {token.lexeme}'
  assert token.literal == literal, f'Wrong token literal found. Expected {literal} had {token.literal}'
  assert token.line == line, f'Wrong token line found. Expected {line} had {token.line}'

class TestLexer:
  def setup_class(self) -> None:
    self._lexer = Lexer()

  def test_scanning_single_tokens(self) -> None:
    tokens: List[Token] = self._lexer.scan('(),.-+*/')

    assert len(tokens) == 9, 'Expected 9 tokens scanned. 8 + EOF'
    assert not self._lexer.errors_detected
    assert_token(tokens[0], TokenType.LEFT_PAREN,   '(', None, 0)    
    assert_token(tokens[1], TokenType.RIGHT_PAREN,  ')', None, 0)    
    assert_token(tokens[2], TokenType.COMMA,        ',', None, 0)    
    assert_token(tokens[3], TokenType.DOT,          '.', None, 0)    
    assert_token(tokens[4], TokenType.MINUS,        '-', None, 0)    
    assert_token(tokens[5], TokenType.PLUS,         '+', None, 0)    
    assert_token(tokens[6], TokenType.STAR,         '*', None, 0)    
    assert_token(tokens[7], TokenType.SLASH,        '/', None, 0)    
    assert_token(tokens[8], TokenType.EOF,          '',  None, 0)    

  def test_scanning_single_operators(self) -> None:
    tokens: List[Token] = self._lexer.scan('=!<>')
    assert len(tokens) == 5, 'Expected 5 tokens scanned. 4 + EOF'
    assert not self._lexer.errors_detected
    assert_token(tokens[0], TokenType.EQUAL,    '=', None, 0) 
    assert_token(tokens[1], TokenType.BANG,     '!', None, 0) 
    assert_token(tokens[2], TokenType.LESS,     '<', None, 0) 
    assert_token(tokens[3], TokenType.GREATER,  '>', None, 0) 
    assert_token(tokens[4], TokenType.EOF,      '',  None, 0) 

  def test_scanning_equality_operators(self) -> None:
    tokens: List[Token] = self._lexer.scan('!= == <= >=')
    assert len(tokens) == 5, 'Expected 5 tokens scanned. 4 + EOF'
    assert not self._lexer.errors_detected
    assert_token(tokens[0], TokenType.BANG_EQUAL,     '!=', None, 0) 
    assert_token(tokens[1], TokenType.EQUAL_EQUAL,    '==', None, 0) 
    assert_token(tokens[2], TokenType.LESS_EQUAL,     '<=', None, 0) 
    assert_token(tokens[3], TokenType.GREATER_EQUAL,  '>=', None, 0) 
    assert_token(tokens[4], TokenType.EOF,            '',   None, 0) 

  def test_scanning_string_literals(self) -> None:
    tokens: List[Token] = self._lexer.scan('"hello world"')
    assert len(tokens) == 2, 'Expected 2 tokens scanned. 1 + EOF'
    assert not self._lexer.errors_detected
    assert_token(tokens[0], TokenType.STRING, '"hello world"', 'hello world', 0) 
    assert_token(tokens[1], TokenType.EOF,    '', None, 0) 
    
    
    more_tokens: List[Token] = self._lexer.scan('\'hello world\'')
    assert len(more_tokens) == 2, 'Expected 2 tokens scanned. 1 + EOF'
    assert not self._lexer.errors_detected
    assert_token(more_tokens[0], TokenType.STRING, '\'hello world\'', 'hello world', 0) 
    assert_token(more_tokens[1], TokenType.EOF,    '', None, 0) 

  def test_scanning_numerical_literals(self) -> None:
    tokens: List[Token] = self._lexer.scan('123 + 456 - 14.92')
    assert len(tokens) == 6, 'Expected 6 tokens scanned. 5 + EOF'
    assert not self._lexer.errors_detected
    assert_token(tokens[0], TokenType.NUMBER, '123', 123, 0) 
    assert_token(tokens[1], TokenType.PLUS,   '+', None, 0) 
    assert_token(tokens[2], TokenType.NUMBER, '456', 456, 0) 
    assert_token(tokens[3], TokenType.MINUS,  '-', None, 0) 
    assert_token(tokens[4], TokenType.NUMBER, '14.92', 14.92, 0) 
    assert_token(tokens[5], TokenType.EOF,    '', None, 0) 

  def test_scanning_identifiers(self) -> None:
    tokens: List[Token] = self._lexer.scan('x = 4')
    assert len(tokens) == 4, 'Expected 4 tokens scanned. 3 + EOF'
    assert not self._lexer.errors_detected
    assert_token(tokens[0], TokenType.IDENTIFIER, 'x', None, 0) 
    assert_token(tokens[1], TokenType.EQUAL, '=', None, 0) 
    assert_token(tokens[2], TokenType.NUMBER, '4', 4, 0) 
    assert_token(tokens[3], TokenType.EOF,    '', None, 0) 
    
    more_tokens: List[Token] = self._lexer.scan('_xyz(4, b)')
    assert len(more_tokens) == 7, 'Expected 7 tokens scanned. 6 + EOF'
    assert not self._lexer.errors_detected
    assert_token(more_tokens[0], TokenType.IDENTIFIER, '_xyz', None, 0) 
    assert_token(more_tokens[1], TokenType.LEFT_PAREN, '(', None, 0) 
    assert_token(more_tokens[2], TokenType.NUMBER, '4', 4, 0) 
    assert_token(more_tokens[3], TokenType.COMMA, ',', None, 0) 
    assert_token(more_tokens[4], TokenType.IDENTIFIER, 'b', None, 0) 
    assert_token(more_tokens[5], TokenType.RIGHT_PAREN, ')', None, 0) 
    assert_token(more_tokens[6], TokenType.EOF,    '', None, 0) 

  def test_scanning_reserved_words(self) -> None:
    tokens: List[Token] = self._lexer.scan('clear True False')
    assert len(tokens) == 4, 'Expected 3 tokens scanned. 1 + EOF'
    assert not self._lexer.errors_detected
    assert_token(tokens[0], TokenType.CLEAR, 'clear', None, 0) 
    assert_token(tokens[1], TokenType.TRUE, 'True', True, 0) 
    assert_token(tokens[2], TokenType.FALSE, 'False', False, 0) 
    assert_token(tokens[3], TokenType.EOF,    '', None, 0) 