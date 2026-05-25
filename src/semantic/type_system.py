class Type:
    def __str__(self):
        return self.__class__.__name__.replace("Type", "").lower()

class IntType(Type): pass
class FloatType(Type): pass
class BoolType(Type): pass
class VoidType(Type): pass
class StringType(Type): pass
class StructType(Type):
    def __init__(self, name):
        self.name = name