import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import Lexer
from src.parser import Parser
from src.parser.ast import ASTVisitor


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
    parser_cli = argparse.ArgumentParser(description='MiniCompiler Parser')
    parser_cli.add_argument('input', nargs='?', help='Input source file')
    parser_cli.add_argument('--mode', choices=['lex', 'parse'], default='parse', help='Operation mode')
    parser_cli.add_argument('--ast-format', choices=['text', 'json', 'dot'], default='text', help='AST output format')
    parser_cli.add_argument('--output', '-o', help='Output file path')
    parser_cli.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser_cli.parse_args()
    
    if not args.input:
        print("Usage: python src/main.py <input_file> [--mode lex|parse] [--ast-format text|json|dot] [-o output] [-v]")
        sys.exit(1)
    
    try:
        source = read_file(args.input)
        
        if args.mode == 'lex':
            lexer = Lexer(source)
            tokens = lexer.scan_tokens()
            output = '\n'.join(str(t) for t in tokens)
        else:
            lexer = Lexer(source)
            tokens = lexer.scan_tokens()
            
            if lexer.errors:
                print(f"Lexer errors: {len(lexer.errors)}", file=sys.stderr)
                sys.exit(1)
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            if parser.errors:
                print(f"Parser errors: {len(parser.errors)}", file=sys.stderr)
                sys.exit(1)
            
            if args.ast_format == 'text':
                printer = PrettyPrinter()
                output = ast.accept(printer)
            elif args.ast_format == 'json':
                def node_to_dict(node):
                    if isinstance(node, list):
                        return [node_to_dict(n) for n in node]
                    if not hasattr(node, '__dict__'):
                        return node
                    result = {'type': node.__class__.__name__}
                    for k, v in node.__dict__.items():
                        if k in ('line', 'column'):
                            result[k] = v
                        elif isinstance(v, (int, float, str, bool, type(None))):
                            result[k] = v
                        elif isinstance(v, list):
                            result[k] = node_to_dict(v)
                        elif hasattr(v, '__dict__'):
                            result[k] = node_to_dict(v)
                    return result
                output = json.dumps(node_to_dict(ast), indent=2)
            else:
                output = f'digraph AST {{\n  node [shape=box];\n'
                node_id = [0]
                def emit_dot(node, parent_id=None):
                    if not hasattr(node, '__dict__'):
                        return
                    my_id = node_id[0]
                    node_id[0] += 1
                    label = node.__class__.__name__
                    if hasattr(node, 'name'):
                        label += f":{node.name}"
                    elif hasattr(node, 'value'):
                        label += f":{node.value}"
                    output_lines.append(f'  n{my_id} [label="{label}"];')
                    if parent_id is not None:
                        output_lines.append(f'  n{parent_id} -> n{my_id};')
                    for k, v in node.__dict__.items():
                        if k in ('line', 'column'):
                            continue
                        if isinstance(v, list):
                            for item in v:
                                emit_dot(item, my_id)
                        elif hasattr(v, '__dict__'):
                            emit_dot(v, my_id)
                output_lines = []
                emit_dot(ast)
                output += '\n'.join(output_lines) + '\n}'
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            if args.verbose:
                print(f"Output written to {args.output}")
        else:
            print(output)
        
        sys.exit(0)
        
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()