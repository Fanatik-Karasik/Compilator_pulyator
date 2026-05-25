class Symbol:
    def __init__(self, name, typ, kind, location):
        self.name = name
        self.type = typ
        self.kind = kind
        self.location = location

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def insert(self, name, symbol):
        if name in self.scopes[-1]:
            raise ValueError(f"Duplicate: {name}")
        self.scopes[-1][name] = symbol

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None