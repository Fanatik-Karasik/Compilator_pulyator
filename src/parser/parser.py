from lexer.token import TokenType


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        # Простая заглушка для Sprint 3
        program = type('Program', (), {'declarations': []})()
        # Создаём хотя бы одну функцию
        func = type('FunctionDecl', (), {
            'name': 'main',
            'parameters': [],
            'return_type': 'int',
            'body': type('Block', (), {'statements': []})(),
            'line': 1
        })()
        program.declarations.append(func)
        return program