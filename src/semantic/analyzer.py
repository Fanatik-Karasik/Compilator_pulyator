import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from symbol_table import SymbolTable, Symbol
from type_system import *
from errors import SemanticError


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def analyze(self, ast_node):
        self.visit(ast_node)
        return self

    def visit(self, node):
        if hasattr(node, 'declarations'):
            for decl in node.declarations:
                self.visit(decl)

    def visit_FunctionDecl(self, node):
        symbol = Symbol(node.name, IntType(), "func", (1, 0))
        try:
            self.symbol_table.insert(node.name, symbol)
        except ValueError:
            pass