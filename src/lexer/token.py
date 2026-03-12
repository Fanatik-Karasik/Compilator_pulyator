from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Union


class TokenType(Enum):
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    KEYWORD_IF = auto()
    KEYWORD_ELSE = auto()
    KEYWORD_WHILE = auto()
    KEYWORD_FOR = auto()
    KEYWORD_INT = auto()
    KEYWORD_FLOAT = auto()
    KEYWORD_BOOL = auto()
    KEYWORD_RETURN = auto()
    KEYWORD_TRUE = auto()
    KEYWORD_FALSE = auto()
    KEYWORD_VOID = auto()
    KEYWORD_STRUCT = auto()
    KEYWORD_FN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    AND = auto()
    OR = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COMMA = auto()
    END_OF_FILE = auto()
    ERROR = auto()


@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int
    value: Optional[Union[int, float, str]] = None
    
    def type_to_string(self) -> str:
        mapping = {
            TokenType.IDENTIFIER: "IDENTIFIER",
            TokenType.INT_LITERAL: "INT_LITERAL",
            TokenType.FLOAT_LITERAL: "FLOAT_LITERAL",
            TokenType.STRING_LITERAL: "STRING_LITERAL",
            TokenType.KEYWORD_IF: "KW_IF",
            TokenType.KEYWORD_ELSE: "KW_ELSE",
            TokenType.KEYWORD_WHILE: "KW_WHILE",
            TokenType.KEYWORD_FOR: "KW_FOR",
            TokenType.KEYWORD_INT: "KW_INT",
            TokenType.KEYWORD_FLOAT: "KW_FLOAT",
            TokenType.KEYWORD_BOOL: "KW_BOOL",
            TokenType.KEYWORD_RETURN: "KW_RETURN",
            TokenType.KEYWORD_TRUE: "KW_TRUE",
            TokenType.KEYWORD_FALSE: "KW_FALSE",
            TokenType.KEYWORD_VOID: "KW_VOID",
            TokenType.KEYWORD_STRUCT: "KW_STRUCT",
            TokenType.KEYWORD_FN: "KW_FN",
            TokenType.PLUS: "PLUS",
            TokenType.MINUS: "MINUS",
            TokenType.STAR: "STAR",
            TokenType.SLASH: "SLASH",
            TokenType.PERCENT: "PERCENT",
            TokenType.ASSIGN: "ASSIGN",
            TokenType.EQUAL: "EQUAL",
            TokenType.NOT_EQUAL: "NOT_EQUAL",
            TokenType.LESS: "LESS",
            TokenType.LESS_EQUAL: "LESS_EQUAL",
            TokenType.GREATER: "GREATER",
            TokenType.GREATER_EQUAL: "GREATER_EQUAL",
            TokenType.AND: "AND",
            TokenType.OR: "OR",
            TokenType.LPAREN: "LPAREN",
            TokenType.RPAREN: "RPAREN",
            TokenType.LBRACE: "LBRACE",
            TokenType.RBRACE: "RBRACE",
            TokenType.SEMICOLON: "SEMICOLON",
            TokenType.COMMA: "COMMA",
            TokenType.END_OF_FILE: "END_OF_FILE",
            TokenType.ERROR: "ERROR",
        }
        return mapping.get(self.type, "UNKNOWN")
    
    def __str__(self) -> str:
        result = f"{self.line}:{self.column} {self.type_to_string()} \"{self.lexeme}\""
        if self.value is not None:
            result += f" {self.value}"
        return result