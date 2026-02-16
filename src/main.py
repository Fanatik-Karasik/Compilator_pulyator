#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import Lexer


def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <input_file>")
        print("Example: python src/main.py examples/hello.src")
        sys.exit(1)

    input_file = sys.argv[1]
    source = read_file(input_file)
    
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    for token in tokens:
        print(token)
    
    if lexer.errors:
        print(f"\nTotal errors: {len(lexer.errors)}")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()