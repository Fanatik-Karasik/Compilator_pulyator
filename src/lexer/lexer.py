from typing import List, Optional
from .token import Token, TokenType


class Lexer:
    KEYWORDS = {
        "if": TokenType.KEYWORD_IF,
        "else": TokenType.KEYWORD_ELSE,
        "while": TokenType.KEYWORD_WHILE,
        "for": TokenType.KEYWORD_FOR,
        "int": TokenType.KEYWORD_INT,
        "float": TokenType.KEYWORD_FLOAT,
        "bool": TokenType.KEYWORD_BOOL,
        "return": TokenType.KEYWORD_RETURN,
        "true": TokenType.KEYWORD_TRUE,
        "false": TokenType.KEYWORD_FALSE,
        "void": TokenType.KEYWORD_VOID,
        "struct": TokenType.KEYWORD_STRUCT,
        "fn": TokenType.KEYWORD_FN,
    }

    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.errors: List[str] = []

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        return char

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def skip_whitespace(self):
        while True:
            char = self.peek()
            if char in ' \r\t':
                self.advance()
            elif char == '\n':
                self.advance()
            elif char == '/' and self.peek_next() == '/':
                self.skip_comment()
            else:
                break

    def skip_comment(self):
        while self.peek() != '\n' and not self.is_at_end():
            self.advance()

    def string(self) -> Token:
        start_col = self.column
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            self.advance()
        if self.is_at_end():
            self.error("Unterminated string.", start_col)
            return Token(TokenType.ERROR, "Unterminated string", self.line, start_col)
        self.advance()
        value = self.source[self.start + 1:self.current - 1]
        lexeme = self.source[self.start:self.current]
        return Token(TokenType.STRING_LITERAL, lexeme, self.line, start_col, value)

    def number(self) -> Token:
        start_col = self.column
        while self.peek().isdigit():
            self.advance()
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
            value = float(self.source[self.start:self.current])
            lexeme = self.source[self.start:self.current]
            return Token(TokenType.FLOAT_LITERAL, lexeme, self.line, start_col, value)
        value = int(self.source[self.start:self.current])
        lexeme = self.source[self.start:self.current]
        return Token(TokenType.INT_LITERAL, lexeme, self.line, start_col, value)

    def identifier(self) -> Token:
        start_col = self.column
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        text = self.source[self.start:self.current]
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        return Token(token_type, text, self.line, start_col)

    def error(self, message: str, column: Optional[int] = None):
        col = column if column else self.column
        error_msg = f"[Error] Line {self.line}:{col} - {message}"
        self.errors.append(error_msg)
        print(error_msg)

    def next_token(self) -> Token:
        self.skip_whitespace()
        self.start = self.current
        start_col = self.column
        if self.is_at_end():
            return Token(TokenType.END_OF_FILE, "", self.line, self.column)
        char = self.advance()
        if char.isalpha() or char == '_':
            self.current -= 1
            self.column -= 1
            return self.identifier()
        if char.isdigit():
            self.current -= 1
            self.column -= 1
            return self.number()
        if char == '"':
            return self.string()
        token_map = {
            '(': TokenType.LPAREN, ')': TokenType.RPAREN,
            '{': TokenType.LBRACE, '}': TokenType.RBRACE,
            ';': TokenType.SEMICOLON, ',': TokenType.COMMA,
            '+': TokenType.PLUS, '-': TokenType.MINUS,
            '*': TokenType.STAR, '%': TokenType.PERCENT,
        }
        if char in token_map:
            return Token(token_map[char], char, self.line, start_col)
        if char == '/':
            return Token(TokenType.SLASH, "/", self.line, start_col)
        if char == '=':
            if self.match('='):
                return Token(TokenType.EQUAL, "==", self.line, start_col)
            return Token(TokenType.ASSIGN, "=", self.line, start_col)
        if char == '!':
            if self.match('='):
                return Token(TokenType.NOT_EQUAL, "!=", self.line, start_col)
            self.error("Unexpected character '!'")
            return Token(TokenType.ERROR, "!", self.line, start_col)
        if char == '<':
            if self.match('='):
                return Token(TokenType.LESS_EQUAL, "<=", self.line, start_col)
            return Token(TokenType.LESS, "<", self.line, start_col)
        if char == '>':
            if self.match('='):
                return Token(TokenType.GREATER_EQUAL, ">=", self.line, start_col)
            return Token(TokenType.GREATER, ">", self.line, start_col)
        if char == '&':
            if self.match('&'):
                return Token(TokenType.AND, "&&", self.line, start_col)
            self.error("Unexpected character '&'")
            return Token(TokenType.ERROR, "&", self.line, start_col)
        if char == '|':
            if self.match('|'):
                return Token(TokenType.OR, "||", self.line, start_col)
            self.error("Unexpected character '|'")
            return Token(TokenType.ERROR, "|", self.line, start_col)
        self.error(f"Unexpected character '{char}'")
        return Token(TokenType.ERROR, char, self.line, start_col)

    def scan_tokens(self) -> List[Token]:
        tokens = []
        while not self.is_at_end():
            token = self.next_token()
            tokens.append(token)
        return tokens