import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import Lexer, TokenType
from src.parser import Parser

TEST_DIR = os.path.join(os.path.dirname(__file__), 'lexer')
PARSER_TEST_DIR = os.path.join(os.path.dirname(__file__), 'parser')
MAIN_SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main.py')


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'


def run_lexer_test(file_path: str, should_fail: bool = False) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        has_errors = len(lexer.errors) > 0
        has_eof = any(t.type == TokenType.END_OF_FILE for t in tokens)
        if should_fail:
            return has_errors
        else:
            return not has_errors and has_eof
    except Exception:
        return False


def run_parser_test(file_path: str, should_fail: bool = False) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        if lexer.errors:
            return should_fail
        parser = Parser(tokens)
        ast = parser.parse()
        has_errors = len(parser.errors) > 0
        if should_fail:
            return has_errors
        else:
            return not has_errors and ast is not None
    except Exception:
        return False


def run_all_tests():
    passed = 0
    failed = 0
    total = 0
    
    print(f"{Colors.YELLOW}Running Lexer Tests...{Colors.RESET}\n")
    
    for category in ['valid', 'invalid']:
        category_path = os.path.join(TEST_DIR, category)
        if not os.path.exists(category_path):
            continue
        should_fail = (category == 'invalid')
        label = "Invalid (should error)" if should_fail else "Valid"
        print(f"{Colors.YELLOW}Category: {label}{Colors.RESET}")
        for filename in sorted(os.listdir(category_path)):
            if not filename.endswith('.src'):
                continue
            file_path = os.path.join(category_path, filename)
            total += 1
            if run_lexer_test(file_path, should_fail):
                print(f"  {Colors.GREEN}✓ PASS{Colors.RESET}: {filename}")
                passed += 1
            else:
                print(f"  {Colors.RED}✗ FAIL{Colors.RESET}: {filename}")
                failed += 1
        print()
    
    print(f"{Colors.YELLOW}Running Parser Tests...{Colors.RESET}\n")
    
    for category in ['valid', 'invalid']:
        category_path = os.path.join(PARSER_TEST_DIR, category)
        if not os.path.exists(category_path):
            continue
        should_fail = (category == 'invalid')
        label = "Invalid (should error)" if should_fail else "Valid"
        print(f"{Colors.YELLOW}Category: {label}{Colors.RESET}")
        for root, dirs, files in os.walk(category_path):
            for filename in sorted(files):
                if not filename.endswith('.src'):
                    continue
                file_path = os.path.join(root, filename)
                total += 1
                if run_parser_test(file_path, should_fail):
                    print(f"  {Colors.GREEN}✓ PASS{Colors.RESET}: {filename}")
                    passed += 1
                else:
                    print(f"  {Colors.RED}✗ FAIL{Colors.RESET}: {filename}")
                    failed += 1
        print()
    
    print(f"{Colors.YELLOW}{'='*50}{Colors.RESET}")
    print(f"Results: {Colors.GREEN}{passed} passed{Colors.RESET}, {Colors.RED}{failed} failed{Colors.RESET} out of {total} tests")
    
    if failed > 0:
        print(f"\n{Colors.RED}Some tests failed!{Colors.RESET}")
        return 1
    else:
        print(f"\n{Colors.GREEN}All tests passed!{Colors.RESET}")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())