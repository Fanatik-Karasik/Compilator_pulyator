from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any
from src.lexer.token import Token, TokenType


class ASTNode(ABC):
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column
    
    @abstractmethod
    def accept(self, visitor: 'ASTVisitor') -> Any:
        pass


class ExpressionNode(ASTNode):
    pass


class StatementNode(ASTNode):
    pass


class DeclarationNode(ASTNode):
    pass


@dataclass
class ProgramNode(ASTNode):
    declarations: List[DeclarationNode] = field(default_factory=list)
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_program(self)


@dataclass
class LiteralExprNode(ExpressionNode):
    value: Any
    literal_type: TokenType
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_literal_expr(self)


@dataclass
class IdentifierExprNode(ExpressionNode):
    name: str
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_identifier_expr(self)


@dataclass
class BinaryExprNode(ExpressionNode):
    left: ExpressionNode
    operator: Token
    right: ExpressionNode
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_binary_expr(self)


@dataclass
class UnaryExprNode(ExpressionNode):
    operator: Token
    operand: ExpressionNode
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_unary_expr(self)


@dataclass
class CallExprNode(ExpressionNode):
    callee: ExpressionNode
    arguments: List[ExpressionNode] = field(default_factory=list)
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_call_expr(self)


@dataclass
class AssignmentExprNode(ExpressionNode):
    target: ExpressionNode
    operator: Token
    value: ExpressionNode
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_assignment_expr(self)


@dataclass
class BlockStmtNode(StatementNode):
    statements: List[StatementNode] = field(default_factory=list)
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_block_stmt(self)


@dataclass
class ExprStmtNode(StatementNode):
    expression: ExpressionNode
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_expr_stmt(self)


@dataclass
class IfStmtNode(StatementNode):
    condition: ExpressionNode
    then_branch: StatementNode
    else_branch: Optional[StatementNode] = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_if_stmt(self)


@dataclass
class WhileStmtNode(StatementNode):
    condition: ExpressionNode
    body: StatementNode
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_while_stmt(self)


@dataclass
class ForStmtNode(StatementNode):
    initializer: Optional[StatementNode]
    condition: Optional[ExpressionNode]
    update: Optional[ExpressionNode]
    body: StatementNode
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_for_stmt(self)


@dataclass
class ReturnStmtNode(StatementNode):
    value: Optional[ExpressionNode] = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_return_stmt(self)


@dataclass
class VarDeclStmtNode(StatementNode, DeclarationNode):
    var_type: str
    name: str
    initializer: Optional[ExpressionNode] = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_var_decl_stmt(self)


@dataclass
class ParamNode(ASTNode):
    param_type: str
    name: str
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_param(self)


@dataclass
class FunctionDeclNode(DeclarationNode):
    return_type: str
    name: str
    parameters: List[ParamNode] = field(default_factory=list)
    body: Optional[BlockStmtNode] = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_function_decl(self)


@dataclass
class StructDeclNode(DeclarationNode):
    name: str
    fields: List[VarDeclStmtNode] = field(default_factory=list)
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_struct_decl(self)


class ASTVisitor(ABC):
    @abstractmethod
    def visit_program(self, node: ProgramNode) -> Any: pass
    @abstractmethod
    def visit_literal_expr(self, node: LiteralExprNode) -> Any: pass
    @abstractmethod
    def visit_identifier_expr(self, node: IdentifierExprNode) -> Any: pass
    @abstractmethod
    def visit_binary_expr(self, node: BinaryExprNode) -> Any: pass
    @abstractmethod
    def visit_unary_expr(self, node: UnaryExprNode) -> Any: pass
    @abstractmethod
    def visit_call_expr(self, node: CallExprNode) -> Any: pass
    @abstractmethod
    def visit_assignment_expr(self, node: AssignmentExprNode) -> Any: pass
    @abstractmethod
    def visit_block_stmt(self, node: BlockStmtNode) -> Any: pass
    @abstractmethod
    def visit_expr_stmt(self, node: ExprStmtNode) -> Any: pass
    @abstractmethod
    def visit_if_stmt(self, node: IfStmtNode) -> Any: pass
    @abstractmethod
    def visit_while_stmt(self, node: WhileStmtNode) -> Any: pass
    @abstractmethod
    def visit_for_stmt(self, node: ForStmtNode) -> Any: pass
    @abstractmethod
    def visit_return_stmt(self, node: ReturnStmtNode) -> Any: pass
    @abstractmethod
    def visit_var_decl_stmt(self, node: VarDeclStmtNode) -> Any: pass
    @abstractmethod
    def visit_param(self, node: ParamNode) -> Any: pass
    @abstractmethod
    def visit_function_decl(self, node: FunctionDeclNode) -> Any: pass
    @abstractmethod
    def visit_struct_decl(self, node: StructDeclNode) -> Any: pass