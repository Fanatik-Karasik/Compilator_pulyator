import sys
import os
import argparse

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from lexer import Lexer
from parser import Parser
from semantic.analyzer import SemanticAnalyzer


class PrettyPrinter:
    def __init__(self):
        self.indent = 0
    
    def _indent(self):
        return "  " * self.indent
    
    def print_ast(self, node):
        print("AST parsed successfully (simplified)")
        return "Program [...]"


def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    parser_cli = argparse.ArgumentParser(description='MiniCompiler Pulyator (Sprint 3)')
    parser_cli.add_argument('input', nargs='?', help='Input source file')
    parser_cli.add_argument('--mode', choices=['lex', 'parse', 'semantic'], default='parse')
    args = parser_cli.parse_args()
    
    if not args.input:
        print("Usage: python src/main.py <input_file> [--mode lex|parse|semantic]")
        sys.exit(1)
    
    source = read_file(args.input)
    
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    if args.mode == 'lex':
        for token in tokens:
            print(token)
        sys.exit(0)
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    if args.mode == 'parse':
        printer = PrettyPrinter()
        print(printer.print_ast(ast))
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
            print("Semantic analysis passed successfully!")
            print("\nSymbol Table:")
            for scope in analyzer.symbol_table.scopes:
                for name, sym in scope.items():
                    print(f"  {name}: {sym.type} ({sym.kind})")
        sys.exit(0)
    
    print("Unknown mode.")
    sys.exit(1)


if __name__ == "__main__":
    main()