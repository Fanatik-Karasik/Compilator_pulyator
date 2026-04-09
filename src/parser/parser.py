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
        if self.is_at_end():
            return self.tokens[-1] if self.tokens else Token(TokenType.EOF, "", None, -1, -1)
        return self.tokens[self.current]

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

        if self.check(TokenType.IDENTIFIER):
            saved = self.current

            self.advance()  
            if self.check(TokenType.IDENTIFIER):
                self.current = saved 
                return self.parse_var_decl()
            else:
                self.current = saved  

        self.error("Ожидается объявление (fn / struct / var).", self.peek())
        return None

    def parse_function_decl(self) -> FunctionDeclNode:
        name_token = self.consume(TokenType.IDENTIFIER, "Ожидается имя функции после 'fn'.")

        self.consume(TokenType.LPAREN, "Ожидается '(' после имени функции.")

        parameters = []
        if not self.check(TokenType.RPAREN):
            while True:
                param_type = self.parse_type()
                param_name_token = self.consume(TokenType.IDENTIFIER, "Ожидается имя параметра.")
                parameters.append(ParamNode(
                    param_name_token.line,
                    param_name_token.column,
                    param_type,
                    param_name_token.lexeme
                ))
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RPAREN, "Ожидается ')' после параметров.")

        return_type = "void"
        if self.match(TokenType.MINUS):
            self.consume(TokenType.GREATER, "Ожидается '->' после '-'.")
            ret_token = self.consume(TokenType.IDENTIFIER, "Ожидается тип возвращаемого значения после '->'.")
            return_type = ret_token.lexeme

        self.consume(TokenType.LBRACE, "Ожидается '{' перед телом функции.")
        body = self.parse_block()

        return FunctionDeclNode(
            name_token.line,
            name_token.column,
            return_type,
            name_token.lexeme,
            parameters,
            body
        )

    def parse_var_decl(self) -> VarDeclStmtNode:
        var_type = self.parse_type()
        name_token = self.consume(TokenType.IDENTIFIER, "Ожидается имя переменной после типа.")
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Ожидается ';' после объявления переменной.")
        return VarDeclStmtNode(
            name_token.line,
            name_token.column,
            var_type,
            name_token.lexeme,
            initializer
        )

    def parse_type(self) -> str:
        token = self.advance()
        if token.type != TokenType.IDENTIFIER:
            self.error(f"Ожидается имя типа, получено {token.type.name} '{token.lexeme}'", token)
            return "unknown"

        type_name = token.lexeme.lower()
        if type_name in ("int", "float", "bool", "string", "void"):
            return type_name
        return token.lexeme

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
            stmt = self.parse_statement()
            statements.append(stmt)
        self.consume(TokenType.RBRACE, "Ожидается '}' после блока.")
        return BlockStmtNode(start_token.line, start_token.column, statements)

    def parse_if_stmt(self) -> IfStmtNode:
        self.consume(TokenType.LPAREN, "Ожидается '(' после 'if'.")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Ожидается ')' после условия.")
        then_branch = self.parse_statement()
        else_branch = None
        if self.match(TokenType.KEYWORD_ELSE):
            else_branch = self.parse_statement()
        return IfStmtNode(condition.line, condition.column, condition, then_branch, else_branch)

    def parse_while_stmt(self) -> WhileStmtNode:
        self.consume(TokenType.LPAREN, "Ожидается '(' после 'while'.")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Ожидается ')' после условия.")
        body = self.parse_statement()
        return WhileStmtNode(condition.line, condition.column, condition, body)

    def parse_for_stmt(self) -> ForStmtNode:
        self.consume(TokenType.LPAREN, "Ожидается '(' после 'for'.")

        initializer = None
        if self.match(TokenType.SEMICOLON):
            pass
        else:
            saved = self.current
            try:
                var_type = self.parse_type()
                if self.check(TokenType.IDENTIFIER):
                    initializer = self.parse_var_decl()
                else:
                    self.current = saved
                    initializer = self.parse_expr_stmt()
            except ParseError:
                self.current = saved
                initializer = self.parse_expr_stmt()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Ожидается ';' после условия цикла.")

        update = None
        if not self.check(TokenType.RPAREN):
            update = self.parse_expression()
        self.consume(TokenType.RPAREN, "Ожидается ')' после заголовка for.")

        body = self.parse_statement()

        line = initializer.line if initializer else self.peek().line
        column = initializer.column if initializer else self.peek().column

        return ForStmtNode(line, column, initializer, condition, update, body)

    def parse_return_stmt(self) -> ReturnStmtNode:
        keyword = self.previous()  # return уже съеден match'ем
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Ожидается ';' после return.")
        return ReturnStmtNode(keyword.line, keyword.column, value)

    def parse_expr_stmt(self) -> ExprStmtNode:
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Ожидается ';' после выражения.")
        return ExprStmtNode(expr.line, expr.column, expr)

    def parse_expression(self) -> ExpressionNode:
        return self.parse_assignment()

    def parse_assignment(self) -> ExpressionNode:
        expr = self.parse_logical_or()
        if self.match(TokenType.ASSIGN):
            equals = self.previous()
            value = self.parse_assignment()
            return AssignmentExprNode(expr.line, expr.column, expr, equals, value)
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
        while True:
            if self.match(TokenType.LPAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def finish_call(self, callee: ExpressionNode) -> CallExprNode:
        arguments = []
        if not self.check(TokenType.RPAREN):
            while True:
                arguments.append(self.parse_expression())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RPAREN, "Ожидается ')' после аргументов.")
        return CallExprNode(callee.line, callee.column, callee, arguments, paren)

    def parse_primary(self) -> ExpressionNode:
        if self.match(TokenType.KEYWORD_TRUE):
            return LiteralExprNode(self.previous().line, self.previous().column, True, "true")
        if self.match(TokenType.KEYWORD_FALSE):
            return LiteralExprNode(self.previous().line, self.previous().column, False, "false")
        if self.match(TokenType.INT_LITERAL):
            return LiteralExprNode(self.previous().line, self.previous().column, self.previous().value, "int")
        if self.match(TokenType.FLOAT_LITERAL):
            return LiteralExprNode(self.previous().line, self.previous().column, self.previous().value, "float")
        if self.match(TokenType.STRING_LITERAL):
            return LiteralExprNode(self.previous().line, self.previous().column, self.previous().value, "string")
        if self.match(TokenType.IDENTIFIER):
            return IdentifierExprNode(self.previous().line, self.previous().column, self.previous().lexeme)
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Ожидается ')' после выражения в скобках.")
            return expr

        raise ParseError("Ожидается выражение.", self.peek())