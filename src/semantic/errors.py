class SemanticError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return f"semantic error: {self.message}"