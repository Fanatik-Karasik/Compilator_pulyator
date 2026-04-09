import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from parser.ast import *
from semantic.symbol_table import SymbolTable, Symbol
from semantic.type_system import *
from semantic.errors import SemanticError


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
            if attr_name.startswith('__') or attr_name.startswith('_'):
                continue
            attr = getattr(node, attr_name, None)
            if isinstance(attr, list):
                for item in attr:
                    self.visit(item)
            elif hasattr(attr, '__class__'):
                self.visit(attr)

    def visit_Program(self, node):
        for decl in node.declarations:
            self.visit(decl)

    def visit_FunctionDecl(self, node):
        return_type = self._parse_type(getattr(node, 'return_type', 'void'))
        symbol = Symbol(node.name, return_type, "func", (getattr(node, 'line', 0), 0))
        try:
            self.symbol_table.insert(node.name, symbol)
        except ValueError:
            self.report(f"duplicate function '{node.name}'", (getattr(node, 'line', 0), 0))

        self.current_function_return_type = return_type
        self.symbol_table.enter_scope()

        for param in getattr(node, 'parameters', []):
            p_type = self._parse_type(getattr(param, 'param_type', getattr(param, 'type', 'int')))
            p_sym = Symbol(param.name, p_type, "param", (getattr(param, 'line', 0), 0))
            try:
                self.symbol_table.insert(param.name, p_sym)
            except ValueError:
                pass

        if hasattr(node, 'body') and node.body:
            self.visit(node.body)
        self.symbol_table.exit_scope()

    def visit_VarDecl(self, node):
        v_type = self._parse_type(getattr(node, 'var_type', getattr(node, 'type', 'int')))
        symbol = Symbol(node.name, v_type, "var", (getattr(node, 'line', 0), 0))
        try:
            self.symbol_table.insert(node.name, symbol)
        except ValueError:
            self.report(f"duplicate variable '{node.name}'", (getattr(node, 'line', 0), 0))

        if hasattr(node, 'initializer') and node.initializer:
            self.visit(node.initializer)

    def visit_IdentifierExpr(self, node):
        sym = self.symbol_table.lookup(node.name)
        if not sym:
            self.report(f"undeclared identifier '{node.name}'", (getattr(node, 'line', 0), 0))
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
        self.visit(node.left)
        self.visit(node.right)
        node.type = IntType()
        return node.type

    def _parse_type(self, t):
        if not t:
            return VoidType()
        t = str(t).lower()
        if t == "int":    return IntType()
        if t == "float":  return FloatType()
        if t == "bool":   return BoolType()
        if t == "void":   return VoidType()
        if t == "string": return StringType()
        return StructType(t)

    def _decorate_ast(self, node):
        pass