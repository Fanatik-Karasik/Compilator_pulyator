from ..parser.ast import *          # Импортируем твои AST-классы (Program, FunctionDecl и т.д.)
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
        # Декорируем AST (DEC-1)
        self._decorate_ast(ast_node)
        return self

    def report(self, msg, location):
        self.errors.append(SemanticError(msg, location))

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in (getattr(node, 'children', []) or []):
            if isinstance(child, list):
                for item in child:
                    self.visit(item)
            else:
                self.visit(child)

    # ------------------- Декларации -------------------
    def visit_Program(self, node):
        for decl in node.declarations:
            self.visit(decl)

    def visit_FunctionDecl(self, node):
        # Проверка дубликатов и типов
        func_type = VoidType() if not node.return_type else self._parse_type(node.return_type)
        symbol = Symbol(node.name, func_type, "func", (node.line, node.col))
        try:
            self.symbol_table.insert(node.name, symbol)
        except ValueError:
            self.report(f"duplicate function '{node.name}'", (node.line, node.col))

        self.current_function_return_type = func_type
        self.symbol_table.enter_scope()

        # Параметры
        for param in node.parameters:
            p_type = self._parse_type(param.type)
            p_sym = Symbol(param.name, p_type, "param", (param.line, param.col))
            self.symbol_table.insert(param.name, p_sym)

        self.visit(node.body)          # Block
        self.symbol_table.exit_scope()
        self.current_function_return_type = None

    def visit_StructDecl(self, node):
        # ... (аналогично, но проще — реализовано минимально)
        pass

    def visit_VarDecl(self, node):
        v_type = self._parse_type(node.type)
        symbol = Symbol(node.name, v_type, "var", (node.line, node.col))
        try:
            self.symbol_table.insert(node.name, symbol)
        except ValueError:
            self.report(f"duplicate variable '{node.name}'", (node.line, node.col))

        if node.init:
            init_type = self.visit(node.init)
            if not is_compatible(v_type, init_type):
                self.report(f"type mismatch: cannot assign {init_type} to {v_type}", (node.line, node.col))

    # ------------------- Выражения -------------------
    def visit_Assignment(self, node):
        # ... (проверка LHS/RHS)
        return self.visit(node.right)

    def visit_Literal(self, node):
        if isinstance(node.value, int):
            node.type = IntType()
        elif isinstance(node.value, float):
            node.type = FloatType()
        elif isinstance(node.value, bool):
            node.type = BoolType()
        return node.type

    def visit_Identifier(self, node):
        sym = self.symbol_table.lookup(node.name)
        if not sym:
            self.report(f"undeclared variable '{node.name}'", (node.line, node.col))
            node.type = IntType()  # fallback
        else:
            node.symbol = sym
            node.type = sym.type
        return node.type


    def _parse_type(self, type_node):
        if type_node == "int": return IntType()
        if type_node == "float": return FloatType()
        if type_node == "bool": return BoolType()
        if type_node == "void": return VoidType()
        if type_node == "string": return StringType()
        return StructType(type_node)

    def _decorate_ast(self, node):
        if hasattr(node, 'type'):
            pass  
        self.generic_visit(node)