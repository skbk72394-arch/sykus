from dataclasses import dataclass
from typing import Any, List, Optional, Dict

class Node: pass
class Statement(Node): pass
class Expression(Node): pass

@dataclass
class Program(Node):
    statements: List[Statement]

@dataclass
class LetStatement(Statement):
    name: str
    value: Expression
    is_const: bool = False

@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression]

@dataclass
class ExpressionStatement(Statement):
    expression: Expression

@dataclass
class BlockStatement(Statement):
    statements: List[Statement]

@dataclass
class IfStatement(Statement):
    condition: Expression
    consequence: BlockStatement
    alternative: Optional[BlockStatement]

@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: BlockStatement

@dataclass
class ForStatement(Statement):
    init: Optional[Statement]
    condition: Optional[Expression]
    update: Optional[Statement]
    body: BlockStatement

@dataclass
class FunctionDeclaration(Statement):
    name: str
    parameters: List[str]
    body: BlockStatement

@dataclass
class ClassDeclaration(Statement):
    name: str
    superclass: Optional[str]
    methods: List[FunctionDeclaration]

@dataclass
class TryCatchStatement(Statement):
    try_block: BlockStatement
    catch_var: str
    catch_block: BlockStatement

@dataclass
class BreakStatement(Statement): pass

@dataclass
class ContinueStatement(Statement): pass

@dataclass
class SayStatement(Statement):
    value: Expression

@dataclass
class AskStatement(Statement):
    prompt: Expression
    name: str

@dataclass
class ImportStatement(Statement):
    file_path: Expression

# Expressions
@dataclass
class Identifier(Expression):
    value: str

@dataclass
class IntegerLiteral(Expression):
    value: int

@dataclass
class FloatLiteral(Expression):
    value: float

@dataclass
class StringLiteral(Expression):
    value: str

@dataclass
class BooleanLiteral(Expression):
    value: bool

@dataclass
class NullLiteral(Expression): pass

@dataclass
class ArrayLiteral(Expression):
    elements: List[Expression]

@dataclass
class HashLiteral(Expression):
    pairs: list # List[Tuple[Expression, Expression]]

@dataclass
class PrefixExpression(Expression):
    operator: str
    right: Expression

@dataclass
class InfixExpression(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class CallExpression(Expression):
    function: Expression
    arguments: List[Expression]

@dataclass
class IndexExpression(Expression):
    left: Expression
    index: Expression

@dataclass
class MemberExpression(Expression):
    obj: Expression
    property: str

@dataclass
class AssignExpression(Expression):
    left: Expression
    value: Expression
