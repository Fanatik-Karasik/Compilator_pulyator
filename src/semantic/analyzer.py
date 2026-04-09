import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser.ast import *
from .symbol_table import SymbolTable, Symbol
from .type_system import *
from .errors import SemanticError


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function_return_type = None

    def analyze(self, ast_node):
        self.visit(ast_node)
        if self.errors:
            return self
        self._decorate_ast(ast_node)
        return self

    def report(self, msg, location=(0, 0)):
        self.errors.append(SemanticError(msg, location))

    def visit(self, node):
        if node is None:
            return None
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for attr_name in dir(node):
            if attr_name.startswith('__'):
                continue
            attr = getattr(node, attr_name)
            if isinstance(attr, list):
                for item in attr:
                    if hasattr(item, 'accept') or hasattr(item, '__class__'):
                        self.visit(item)
            elif hasattr(attr, 'accept') or hasattr(attr, '__class__'):
                self.visit(attr)

    # Основные визиторы
    def visit_Program(self, node):
        for decl in node.declarations:
            self.visit(decl)

    def visit_FunctionDecl(self, node):
        return_type = self._parse_type(node.return_type)
        symbol = Symbol(node.name, return_type, "func", (node.line, getattr(node, 'col', 0)))
        try:
            self.symbol_table.insert(node.name, symbol)
        except ValueError:
            self.report(f"duplicate function '{node.name}'", (node.line, getattr(node, 'col', 0)))

        self.current_function_return_type = return_type
        self.symbol_table.enter_scope()

        for param in node.parameters:
            p_type = self._parse_type(param.param_type if hasattr(param, 'param_type') else param.type)
            p_sym = Symbol(param.name, p_type, "param", (getattr(param, 'line', 0), 0))
            try:
                self.symbol_table.insert(param.name, p_sym)
            except ValueError:
                self.report(f"duplicate parameter '{param.name}'", (getattr(param, 'line', 0), 0))

        self.visit(node.body)
        self.symbol_table.exit_scope()

    def visit_VarDecl(self, node):
        v_type = self._parse_type(node.var_type if hasattr(node, 'var_type') else node.type)
        symbol = Symbol(node.name, v_type, "var", (node.line, getattr(node, 'col', 0)))
        try:
            self.symbol_table.insert(node.name, symbol)
        except ValueError:
            self.report(f"duplicate variable '{node.name}'", (node.line, getattr(node, 'col', 0)))

        if hasattr(node, 'initializer') and node.initializer:
            init_type = self.visit(node.initializer)
            if init_type and not is_compatible(v_type, init_type):
                self.report(f"type mismatch: cannot assign to {v_type}", (node.line, 0))

    def visit_IdentifierExpr(self, node):
        sym = self.symbol_table.lookup(node.name)
        if not sym:
            self.report(f"undeclared identifier '{node.name}'", (node.line, getattr(node, 'col', 0)))
            node.type = IntType()
        else:
            node.symbol = sym
            node.type = sym.type
        return node.type

    def visit_LiteralExpr(self, node):
        if isinstance(node.value, int):
            node.type = IntType()
        elif isinstance(node.value, float):
            node.type = FloatType()
        elif isinstance(node.value, bool):
            node.type = BoolType()
        else:
            node.type = StringType()
        return node.type

    def visit_BinaryExpr(self, node):
        left_t = self.visit(node.left)
        right_t = self.visit(node.right)
        if left_t and right_t and not is_compatible(left_t, right_t):
            self.report("incompatible types in binary expression", (node.line, 0))
        node.type = left_t or IntType()
        return node.type

    def _parse_type(self, t):
        if not t:
            return VoidType()
        t = str(t).lower()
        if t == "int": return IntType()
        if t == "float": return FloatType()
        if t == "bool": return BoolType()
        if t == "void": return VoidType()
        if t == "string": return StringType()
        return StructType(t)

    def _decorate_ast(self, node):
        pass  


def main_test():
    """Для быстрой проверки"""
    pass