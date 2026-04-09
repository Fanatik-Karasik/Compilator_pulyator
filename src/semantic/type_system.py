class Symbol:
    def __init__(self, name, typ, kind, location):
        self.name = name
        self.type = typ
        self.kind = kind          # "var", "param", "func", "struct"
        self.location = location  # (line, col)
        self.scope_depth = 0

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]        # глобальный скоуп
        self.current_depth = 0

    def enter_scope(self):
        self.scopes.append({})
        self.current_depth += 1

    def exit_scope(self):
        self.scopes.pop()
        self.current_depth -= 1

    def insert(self, name, symbol):
        if name in self.scopes[-1]:
            raise ValueError(f"Duplicate declaration: {name}")
        symbol.scope_depth = self.current_depth
        self.scopes[-1][name] = symbol

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_local(self, name):
        return self.scopes[-1].get(name)