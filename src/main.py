import sys
import os
import argparse

from src.lexer import Lexer
from src.parser import Parser
from src.parser.ast import ASTVisitor
from src.semantic.analyzer import SemanticAnalyzer

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)



class PrettyPrinter(ASTVisitor):
    def __init__(self):
        self.indent = 0
    
    def _indent(self):
        return "  " * self.indent
    
    def visit_program(self, node):
        result = f"{self._indent()}Program [line {node.line}]:\n"
        self.indent += 1
        for decl in node.declarations:
            result += decl.accept(self)
        self.indent -= 1
        return result
    
    def visit_literal_expr(self, node):
        return f"{self._indent()}Literal: {node.value} [line {node.line}]\n"
    
    def visit_identifier_expr(self, node):
        return f"{self._indent()}Identifier: {node.name} [line {node.line}]\n"
    
    def visit_binary_expr(self, node):
        result = f"{self._indent()}Binary: {node.operator.lexeme} [line {node.line}]:\n"
        self.indent += 1
        result += node.left.accept(self)
        result += node.right.accept(self)
        self.indent -= 1
        return result
    
    def visit_unary_expr(self, node):
        result = f"{self._indent()}Unary: {node.operator.lexeme} [line {node.line}]:\n"
        self.indent += 1
        result += node.operand.accept(self)
        self.indent -= 1
        return result
    
    def visit_call_expr(self, node):
        result = f"{self._indent()}Call [line {node.line}]:\n"
        self.indent += 1
        result += node.callee.accept(self)
        for arg in node.arguments:
            result += arg.accept(self)
        self.indent -= 1
        return result
    
    def visit_assignment_expr(self, node):
        result = f"{self._indent()}Assignment: {node.operator.lexeme} [line {node.line}]:\n"
        self.indent += 1
        result += node.target.accept(self)
        result += node.value.accept(self)
        self.indent -= 1
        return result
    
    def visit_block_stmt(self, node):
        result = f"{self._indent()}Block [line {node.line}]:\n"
        self.indent += 1
        for stmt in node.statements:
            result += stmt.accept(self)
        self.indent -= 1
        return result
    
    def visit_expr_stmt(self, node):
        return node.expression.accept(self)
    
    def visit_if_stmt(self, node):
        result = f"{self._indent()}If [line {node.line}]:\n"
        self.indent += 1
        result += f"{self._indent()}Condition:\n"
        self.indent += 1
        result += node.condition.accept(self)
        self.indent -= 2
        result += f"{self._indent()}Then:\n"
        self.indent += 1
        result += node.then_branch.accept(self)
        self.indent -= 1
        if node.else_branch:
            result += f"{self._indent()}Else:\n"
            self.indent += 1
            result += node.else_branch.accept(self)
            self.indent -= 1
        self.indent -= 1
        return result
    
    def visit_while_stmt(self, node):
        result = f"{self._indent()}While [line {node.line}]:\n"
        self.indent += 1
        result += f"{self._indent()}Condition:\n"
        self.indent += 1
        result += node.condition.accept(self)
        self.indent -= 2
        result += f"{self._indent()}Body:\n"
        self.indent += 1
        result += node.body.accept(self)
        self.indent -= 2
        return result
    
    def visit_for_stmt(self, node):
        result = f"{self._indent()}For [line {node.line}]:\n"
        self.indent += 1
        if node.initializer:
            result += f"{self._indent()}Init:\n"
            self.indent += 1
            result += node.initializer.accept(self)
            self.indent -= 1
        if node.condition:
            result += f"{self._indent()}Condition:\n"
            self.indent += 1
            result += node.condition.accept(self)
            self.indent -= 1
        if node.update:
            result += f"{self._indent()}Update:\n"
            self.indent += 1
            result += node.update.accept(self)
            self.indent -= 1
        result += f"{self._indent()}Body:\n"
        self.indent += 1
        result += node.body.accept(self)
        self.indent -= 2
        return result
    
    def visit_return_stmt(self, node):
        result = f"{self._indent()}Return [line {node.line}]:\n"
        if node.value:
            self.indent += 1
            result += node.value.accept(self)
            self.indent -= 1
        return result
    
    def visit_var_decl_stmt(self, node):
        result = f"{self._indent()}VarDecl: {node.var_type} {node.name}"
        if node.initializer:
            result += " = "
            self.indent += 1
            result += node.initializer.accept(self).strip()
            self.indent -= 1
        result += f" [line {node.line}]\n"
        return result
    
    def visit_param(self, node):
        return f"{self._indent()}Param: {node.param_type} {node.name} [line {node.line}]\n"
    
    def visit_function_decl(self, node):
        result = f"{self._indent()}FunctionDecl: {node.name} -> {node.return_type} [line {node.line}]:\n"
        self.indent += 1
        result += f"{self._indent()}Parameters:\n"
        self.indent += 1
        for param in node.parameters:
            result += param.accept(self)
        self.indent -= 2
        if node.body:
            result += f"{self._indent()}Body:\n"
            result += node.body.accept(self)
        self.indent -= 1
        return result
    
    def visit_struct_decl(self, node):
        result = f"{self._indent()}StructDecl: {node.name} [line {node.line}]:\n"
        self.indent += 1
        for field in node.fields:
            result += field.accept(self)
        self.indent -= 1
        return result


def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    parser_cli = argparse.ArgumentParser(description='MiniCompiler Pulyator (Sprint 3)')
    parser_cli.add_argument('input', nargs='?', help='Input source file')
    parser_cli.add_argument('--mode', choices=['lex', 'parse', 'semantic'], default='parse',
                            help='Operation mode: lex | parse | semantic')
    parser_cli.add_argument('--ast-format', choices=['text', 'json', 'dot'], default='text',
                            help='AST output format (only for parse mode)')
    parser_cli.add_argument('--output', '-o', help='Output file path')
    parser_cli.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser_cli.parse_args()
    
    if not args.input:
        print("Usage: python src/main.py <input_file> [--mode lex|parse|semantic] [--ast-format text|json|dot]")
        sys.exit(1)
    
    source = read_file(args.input)
    
    lexer = Lexer(source, args.input)
    tokens = lexer.tokenize()
    
    if args.mode == 'lex':
        for token in tokens:
            print(token)
        if args.verbose:
            print(f"\nLexed {len(tokens)} tokens")
        sys.exit(0)
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    if args.mode == 'parse':
        if args.ast_format == 'text':
            printer = PrettyPrinter()
            print(ast.accept(printer))
        else:
            print(f"AST format '{args.ast_format}' not implemented yet.")
        sys.exit(0)
    
    if args.mode == 'semantic':
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        if analyzer.errors:
            for err in analyzer.errors:
                print(err)
            print(f"\nFound {len(analyzer.errors)} semantic error(s)")
            sys.exit(1)
        else:
            print(" Semantic analysis passed successfully!")
            print("\nSymbol Table:")
            for scope in analyzer.symbol_table.scopes:
                for name, sym in scope.items():
                    print(f"  {name}: {sym.type} ({sym.kind}) depth={sym.scope_depth}")
        sys.exit(0)
    
    print("Unknown mode. Use --mode lex|parse|semantic")
    sys.exit(1)


if __name__ == "__main__":
    main()