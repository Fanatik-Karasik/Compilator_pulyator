class SemanticError(Exception):
    def __init__(self, message, location=None):
        self.message = message
        self.location = location or (0, 0)
        super().__init__(self.message)

    def __str__(self):
        line, col = self.location
        return f"semantic error: {self.message}\n--> program.src:{line}:{col}"