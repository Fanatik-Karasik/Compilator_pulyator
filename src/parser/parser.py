from typing import List, Optional, Any
from src.lexer.token import Token, TokenType
from src.lexer.lexer import Lexer
from .ast import (
    ASTNode, ProgramNode, ExpressionNode, StatementNode, DeclarationNode,
    LiteralExprNode, IdentifierExprNode, BinaryExprNode, UnaryExprNode,
    CallExprNode, AssignmentExprNode, BlockStmtNode, ExprStmtNode,
    IfStmtNode, WhileStmtNode, ForStmtNode, ReturnStmtNode,
    VarDeclStmtNode, ParamNode, FunctionDeclNode, StructDeclNode
)


class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"[Parse Error] Line {token.line}:{token.column} - {message}")


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors: List[str] = []

    def peek(self) -> Token:
        return self.tokens[self.current] if not self.is_at_end() else self.tokens[-1]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def check(self, *types: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type in types

    def match(self, *types: TokenType) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise ParseError(message, self.peek())

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in [
                TokenType.KEYWORD_FN, TokenType.KEYWORD_STRUCT,
                TokenType.KEYWORD_IF, TokenType.KEYWORD_WHILE,
                TokenType.KEYWORD_FOR, TokenType.KEYWORD_RETURN,
                TokenType.LBRACE, TokenType.RBRACE
            ]:
                return
            self.advance()

    def error(self, message: str, token: Token):
        error_msg = f"[Parse Error] Line {token.line}:{token.column} - {message}"
        self.errors.append(error_msg)
        print(error_msg)

    def parse(self) -> ProgramNode:
        declarations = []
        while not self.is_at_end():
            try:
                decl = self.parse_declaration()
                if decl:
                    declarations.append(decl)
            except ParseError as e:
                self.error(e.message, e.token)
                self.synchronize()
        return ProgramNode(self.peek().line, self.peek().column, declarations)

    def parse_declaration(self) -> Optional[DeclarationNode]:
        if self.match(TokenType.KEYWORD_FN):
            return self.parse_function_decl()
        if self.match(TokenType.KEYWORD_STRUCT):
            return self.parse_struct_decl()
        if self.check(TokenType.KEYWORD_INT, TokenType.KEYWORD_FLOAT, 
                     TokenType.KEYWORD_BOOL, TokenType.KEYWORD_VOID,
                     TokenType.IDENTIFIER):
            return self.parse_var_decl()
        return None

    def parse_function_decl(self) -> FunctionDeclNode:
        name_token = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        self.consume(TokenType.LPAREN, "Expect '(' after function name.")
        parameters = []
        if not self.check(TokenType.RPAREN):
            while True:
                param_type = self.parse_type()
                param_name = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                parameters.append(ParamNode(param_name.line, param_name.column, param_type, param_name.lexeme))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
        return_type = "void"
        if self.match(TokenType.SLASH):
            if not self.match(TokenType.GREATER):
                raise ParseError("Expect '->' for return type.", self.previous())
            return_type = self.parse_type()
        body = self.parse_block()
        return FunctionDeclNode(name_token.line, name_token.column, return_type, name_token.lexeme, parameters, body)

    def parse_struct_decl(self) -> StructDeclNode:
        name_token = self.consume(TokenType.IDENTIFIER, "Expect struct name.")
        self.consume(TokenType.LBRACE, "Expect '{' before struct fields.")
        fields = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            field_decl = self.parse_var_decl()
            if field_decl:
                fields.append(field_decl)
        self.consume(TokenType.RBRACE, "Expect '}' after struct fields.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after struct declaration.")
        return StructDeclNode(name_token.line, name_token.column, name_token.lexeme, fields)

    def parse_var_decl(self) -> Optional[VarDeclStmtNode]:
        var_type = self.parse_type()
        if not self.check(TokenType.IDENTIFIER):
            self.current -= 1
            return None
        name_token = self.advance()
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarDeclStmtNode(name_token.line, name_token.column, var_type, name_token.lexeme, initializer)

    def parse_type(self) -> str:
        if self.match(TokenType.KEYWORD_INT):
            return "int"
        if self.match(TokenType.KEYWORD_FLOAT):
            return "float"
        if self.match(TokenType.KEYWORD_BOOL):
            return "bool"
        if self.match(TokenType.KEYWORD_VOID):
            return "void"
        type_token = self.consume(TokenType.IDENTIFIER, "Expect type name.")
        return type_token.lexeme

    def parse_statement(self) -> StatementNode:
        if self.match(TokenType.KEYWORD_IF):
            return self.parse_if_stmt()
        if self.match(TokenType.KEYWORD_WHILE):
            return self.parse_while_stmt()
        if self.match(TokenType.KEYWORD_FOR):
            return self.parse_for_stmt()
        if self.match(TokenType.KEYWORD_RETURN):
            return self.parse_return_stmt()
        if self.match(TokenType.LBRACE):
            return self.parse_block()
        return self.parse_expr_stmt()

    def parse_block(self) -> BlockStmtNode:
        start_token = self.previous()
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.parse_statement())
        self.consume(TokenType.RBRACE, "Expect '}' after block.")
        return BlockStmtNode(start_token.line, start_token.column, statements)

    def parse_if_stmt(self) -> IfStmtNode:
        self.consume(TokenType.LPAREN, "Expect '(' after 'if'.")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after condition.")
        then_branch = self.parse_statement()
        else_branch = None
        if self.match(TokenType.KEYWORD_ELSE):
            else_branch = self.parse_statement()
        return IfStmtNode(condition.line, condition.column, condition, then_branch, else_branch)

    def parse_while_stmt(self) -> WhileStmtNode:
        self.consume(TokenType.LPAREN, "Expect '(' after 'while'.")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after condition.")
        body = self.parse_statement()
        return WhileStmtNode(condition.line, condition.column, condition, body)

    def parse_for_stmt(self) -> ForStmtNode:
        self.consume(TokenType.LPAREN, "Expect '(' after 'for'.")
        initializer = None
        if self.match(TokenType.SEMICOLON):
            pass
        elif self.check(TokenType.KEYWORD_INT, TokenType.KEYWORD_FLOAT, 
                       TokenType.KEYWORD_BOOL, TokenType.IDENTIFIER):
            initializer = self.parse_var_decl()
        else:
            initializer = self.parse_expr_stmt()
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        update = None
        if not self.check(TokenType.RPAREN):
            update = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after for clauses.")
        body = self.parse_statement()
        return ForStmtNode(
            initializer.line if initializer else self.peek().line,
            initializer.column if initializer else self.peek().column,
            initializer, condition, update, body
        )

    def parse_return_stmt(self) -> ReturnStmtNode:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStmtNode(keyword.line, keyword.column, value)

    def parse_expr_stmt(self) -> ExprStmtNode:
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExprStmtNode(expr.line, expr.column, expr)

    def parse_expression(self) -> ExpressionNode:
        return self.parse_assignment()

    def parse_assignment(self) -> ExpressionNode:
        expr = self.parse_logical_or()
        if self.match(TokenType.ASSIGN):
            operator = self.previous()
            value = self.parse_assignment()
            return AssignmentExprNode(expr.line, expr.column, expr, operator, value)
        return expr

    def parse_logical_or(self) -> ExpressionNode:
        expr = self.parse_logical_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.parse_logical_and()
            expr = BinaryExprNode(expr.line, expr.column, expr, operator, right)
        return expr

    def parse_logical_and(self) -> ExpressionNode:
        expr = self.parse_equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.parse_equality()
            expr = BinaryExprNode(expr.line, expr.column, expr, operator, right)
        return expr

    def parse_equality(self) -> ExpressionNode:
        expr = self.parse_relational()
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous()
            right = self.parse_relational()
            expr = BinaryExprNode(expr.line, expr.column, expr, operator, right)
        return expr

    def parse_relational(self) -> ExpressionNode:
        expr = self.parse_additive()
        while self.match(TokenType.LESS, TokenType.LESS_EQUAL, 
                        TokenType.GREATER, TokenType.GREATER_EQUAL):
            operator = self.previous()
            right = self.parse_additive()
            expr = BinaryExprNode(expr.line, expr.column, expr, operator, right)
        return expr

    def parse_additive(self) -> ExpressionNode:
        expr = self.parse_multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.parse_multiplicative()
            expr = BinaryExprNode(expr.line, expr.column, expr, operator, right)
        return expr

    def parse_multiplicative(self) -> ExpressionNode:
        expr = self.parse_unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self.previous()
            right = self.parse_unary()
            expr = BinaryExprNode(expr.line, expr.column, expr, operator, right)
        return expr

    def parse_unary(self) -> ExpressionNode:
        if self.match(TokenType.MINUS, TokenType.BANG):
            operator = self.previous()
            right = self.parse_unary()
            return UnaryExprNode(operator.line, operator.column, operator, right)
        return self.parse_call()

    def parse_call(self) -> ExpressionNode:
        expr = self.parse_primary()
        while self.match(TokenType.LPAREN):
            expr = self.finish_call(expr)
        return expr

    def finish_call(self, callee: ExpressionNode) -> CallExprNode:
        arguments = []
        if not self.check(TokenType.RPAREN):
            while True:
                arguments.append(self.parse_expression())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RPAREN, "Expect ')' after arguments.")
        return CallExprNode(callee.line, callee.column, callee, arguments)

    def parse_primary(self) -> ExpressionNode:
        if self.match(TokenType.KEYWORD_TRUE):
            return LiteralExprNode(self.previous().line, self.previous().column, True, TokenType.KEYWORD_TRUE)
        if self.match(TokenType.KEYWORD_FALSE):
            return LiteralExprNode(self.previous().line, self.previous().column, False, TokenType.KEYWORD_FALSE)
        if self.match(TokenType.INT_LITERAL):
            return LiteralExprNode(self.previous().line, self.previous().column, self.previous().value, TokenType.INT_LITERAL)
        if self.match(TokenType.FLOAT_LITERAL):
            return LiteralExprNode(self.previous().line, self.previous().column, self.previous().value, TokenType.FLOAT_LITERAL)
        if self.match(TokenType.STRING_LITERAL):
            return LiteralExprNode(self.previous().line, self.previous().column, self.previous().value, TokenType.STRING_LITERAL)
        if self.match(TokenType.IDENTIFIER):
            return IdentifierExprNode(self.previous().line, self.previous().column, self.previous().lexeme)
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression.")
            return expr
        raise ParseError("Expect expression.", self.peek())