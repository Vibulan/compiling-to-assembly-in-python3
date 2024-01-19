import re
from enum import StrEnum, auto
from AST import *

class TokenType(StrEnum):
    NUMBER = auto()
    IDENTIFIER = auto()
    NOT = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOTEQUAL = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    LBRACE = auto()
    RBRACE = auto()
    LPAREN = auto()
    RPAREN = auto()
    RETURN = auto()
    SEMICOLON = auto()
    IF = auto()
    ELSE = auto()
    FUNCTION = auto()
    VAR = auto()
    WHILE = auto()
    COMMA = auto()

class Token:
    def __init__(self, type:TokenType, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f'Token({self.type},{self.value})'

    def __eq__(self, other):
        if(type(self) is type(other)):
            return self.__dict__ == other.__dict__
        else:
            return self.type == other

class Lexer:
    def __init__(self, text:str):
        self.text = text
        self.pos = 0

        self.patterns = [
            (r'return', TokenType.RETURN),
            (r';', TokenType.SEMICOLON),
            (r'if', TokenType.IF),
            (r'else', TokenType.ELSE),
            (r'function', TokenType.FUNCTION),
            (r'var', TokenType.VAR),
            (r'while', TokenType.WHILE),
            (r'\d+', TokenType.NUMBER),
            (r'!=', TokenType.NOTEQUAL),        
            (r'={2}', TokenType.EQUAL),
            (r',', TokenType.COMMA),
            (r'!', TokenType.NOT),
            (r'=', TokenType.ASSIGN),
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.STAR),
            (r'/', TokenType.SLASH),
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER)
        ]

    def error(self):
        raise Exception(f'Invalid character at position {self.pos}: {self.text[self.pos]}')

    def get_next_token(self):
        # Skip Whitespace and comments
        while self.pos < len(self.text) and (self.text[self.pos].isspace() or self.text[self.pos:self.pos + 2] == '//'):
            if self.text[self.pos:self.pos + 2] == '//':
                self.pos = self.text.find('\n', self.pos)
                if self.pos == -1:
                    self.pos = len(self.text)
            else:
                self.pos += 1

        if self.pos >= len(self.text):
            return Token('EOF')

        # Token patterns using regular expressions
        for pattern, token_type in self.patterns:
            regex = re.compile(pattern)
            match = regex.match(self.text, self.pos)

            if match:
                value = match.group()
                token = Token(token_type, value)
                self.pos = match.end()
                return token

        self.error()

    def peek_next_token(self):
        # Skip Whitespace and comments
        pos = self.pos
        while pos < len(self.text) and (self.text[pos].isspace() or self.text[pos:pos + 2] == '//'):
            if self.text[pos:pos + 2] == '//':
                pos = self.text.find('\n', pos)
                if pos == -1:
                    pos = len(self.text)
            else:
                pos += 1

        if pos >= len(self.text):
            return Token('EOF')

        # Token patterns using regular expressions
        for pattern, token_type in self.patterns:
            regex = re.compile(pattern)
            match = regex.match(self.text, pos)

            if match:
                value = match.group()
                token = Token(token_type, value)
                return token

        self.error()

    def get_current_line_in_source(self):
        position = self.pos
        start_index = self.text.rfind('\n', 0, position) + 1 if '\n' in self.text[:position] else 0

        # Find the end index of the line
        end_index = self.text.find('\n', position)
        end_index = end_index if end_index != -1 else len(self.text)

        # Extract and print the line
        return self.text[start_index:end_index]



if __name__ == '__main__':

    text =  '''
        function main() {
            assert(1);
        }
        '''
    lexer = Lexer(text)

    print(Token(TokenType.NUMBER, 2) == TokenType.NUMBER)

    try:
        while True:
            token = lexer.get_next_token()
            if token.type == 'EOF':
                break
            print(token)
    except Exception as e:
        print(e)