import os

os.makedirs('src', exist_ok=True)

with open('src/__init__.py', 'w') as f:
    pass

with open('src/ast.py', 'w') as f:
    f.write('''from dataclasses import dataclass
from typing import Any, List, Optional

class Node: pass
class Statement(Node): pass
class Expression(Node): pass

@dataclass class Program(Node):
    statements: List[Statement]

@dataclass class LetStatement(Statement):
    name: str
    value: Expression
    is_const: bool = False

@dataclass class ReturnStatement(Statement):
    value: Optional[Expression]

@dataclass class ExpressionStatement(Statement):
    expression: Expression

@dataclass class BlockStatement(Statement):
    statements: List[Statement]

@dataclass class IfStatement(Statement):
    condition: Expression
    consequence: BlockStatement
    alternative: Optional[BlockStatement]

@dataclass class WhileStatement(Statement):
    condition: Expression
    body: BlockStatement

@dataclass class FunctionDeclaration(Statement):
    name: str
    parameters: List[str]
    body: BlockStatement

@dataclass class ClassDeclaration(Statement):
    name: str
    superclass: Optional[str]
    methods: List[FunctionDeclaration]

@dataclass class TryCatchStatement(Statement):
    try_block: BlockStatement
    catch_var: str
    catch_block: BlockStatement

@dataclass class BreakStatement(Statement): pass
@dataclass class ContinueStatement(Statement): pass
@dataclass class SayStatement(Statement):
    value: Expression

# Expressions
@dataclass class Identifier(Expression):
    value: str

@dataclass class IntegerLiteral(Expression):
    value: int

@dataclass class FloatLiteral(Expression):
    value: float

@dataclass class StringLiteral(Expression):
    value: str

@dataclass class BooleanLiteral(Expression):
    value: bool

@dataclass class NullLiteral(Expression): pass

@dataclass class ArrayLiteral(Expression):
    elements: List[Expression]

@dataclass class HashLiteral(Expression):
    pairs: dict # Expression -> Expression

@dataclass class PrefixExpression(Expression):
    operator: str
    right: Expression

@dataclass class InfixExpression(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass class CallExpression(Expression):
    function: Expression
    arguments: List[Expression]

@dataclass class IndexExpression(Expression):
    left: Expression
    index: Expression

@dataclass class MemberExpression(Expression):
    obj: Expression
    property: str

@dataclass class AssignExpression(Expression):
    left: Expression
    value: Expression
''')

with open('src/tokenizer.py', 'w') as f:
    f.write('''import re
from dataclasses import dataclass

TokenType = str

@dataclass
class Token:
    type: TokenType
    literal: str
    line: int
    column: int

class TokenTypeList:
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"
    IDENT = "IDENT"
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    BANG = "!"
    ASTERISK = "*"
    SLASH = "/"
    LT = "<"
    GT = ">"
    EQ = "=="
    NOT_EQ = "!="
    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    DOT = "."
    
    # Keywords
    FUNCTION = "FUNCTION"
    LET = "LET"
    CONST = "CONST"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"
    WHILE = "WHILE"
    FOR = "FOR"
    CLASS = "CLASS"
    TRY = "TRY"
    CATCH = "CATCH"
    NULL = "NULL"
    SAY = "SAY"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"

KEYWORDS = {
    "func": TokenTypeList.FUNCTION,
    "let": TokenTypeList.LET,
    "const": TokenTypeList.CONST,
    "true": TokenTypeList.TRUE,
    "false": TokenTypeList.FALSE,
    "if": TokenTypeList.IF,
    "else": TokenTypeList.ELSE,
    "return": TokenTypeList.RETURN,
    "while": TokenTypeList.WHILE,
    "for": TokenTypeList.FOR,
    "class": TokenTypeList.CLASS,
    "try": TokenTypeList.TRY,
    "catch": TokenTypeList.CATCH,
    "null": TokenTypeList.NULL,
    "say": TokenTypeList.SAY,
    "break": TokenTypeList.BREAK,
    "continue": TokenTypeList.CONTINUE
}

class Lexer:
    def __init__(self, input_code: str):
        self.input = input_code
        self.position = 0
        self.read_position = 0
        self.ch = ''
        self.line = 1
        self.column = 0
        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = '\\0'
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1
        self.column += 1

    def peek_char(self):
        if self.read_position >= len(self.input):
            return '\\0'
        return self.input[self.read_position]

    def next_token(self) -> Token:
        self.skip_whitespace()
        
        tok = None
        current_col = self.column
        current_line = self.line

        if self.ch == '=':
            if self.peek_char() == '=':
                self.read_char()
                tok = Token(TokenTypeList.EQ, "==", current_line, current_col)
            else:
                tok = Token(TokenTypeList.ASSIGN, self.ch, current_line, current_col)
        elif self.ch == '+':
            tok = Token(TokenTypeList.PLUS, self.ch, current_line, current_col)
        elif self.ch == '-':
            tok = Token(TokenTypeList.MINUS, self.ch, current_line, current_col)
        elif self.ch == '!':
            if self.peek_char() == '=':
                self.read_char()
                tok = Token(TokenTypeList.NOT_EQ, "!=", current_line, current_col)
            else:
                tok = Token(TokenTypeList.BANG, self.ch, current_line, current_col)
        elif self.ch == '/':
            if self.peek_char() == '/':
                self.skip_comment()
                return self.next_token()
            else:
                tok = Token(TokenTypeList.SLASH, self.ch, current_line, current_col)
        elif self.ch == '*':
            tok = Token(TokenTypeList.ASTERISK, self.ch, current_line, current_col)
        elif self.ch == '<':
            tok = Token(TokenTypeList.LT, self.ch, current_line, current_col)
        elif self.ch == '>':
            tok = Token(TokenTypeList.GT, self.ch, current_line, current_col)
        elif self.ch == ';':
            tok = Token(TokenTypeList.SEMICOLON, self.ch, current_line, current_col)
        elif self.ch == ':':
            tok = Token(TokenTypeList.COLON, self.ch, current_line, current_col)
        elif self.ch == ',':
            tok = Token(TokenTypeList.COMMA, self.ch, current_line, current_col)
        elif self.ch == '(':
            tok = Token(TokenTypeList.LPAREN, self.ch, current_line, current_col)
        elif self.ch == ')':
            tok = Token(TokenTypeList.RPAREN, self.ch, current_line, current_col)
        elif self.ch == '{':
            tok = Token(TokenTypeList.LBRACE, self.ch, current_line, current_col)
        elif self.ch == '}':
            tok = Token(TokenTypeList.RBRACE, self.ch, current_line, current_col)
        elif self.ch == '[':
            tok = Token(TokenTypeList.LBRACKET, self.ch, current_line, current_col)
        elif self.ch == ']':
            tok = Token(TokenTypeList.RBRACKET, self.ch, current_line, current_col)
        elif self.ch == '.':
            tok = Token(TokenTypeList.DOT, self.ch, current_line, current_col)
        elif self.ch == '"' or self.ch == "\\'":
            tok = Token(TokenTypeList.STRING, self.read_string(self.ch), current_line, current_col)
        elif self.ch == '\\0':
            tok = Token(TokenTypeList.EOF, "", current_line, current_col)
        else:
            if self.is_letter(self.ch):
                literal = self.read_identifier()
                token_type = KEYWORDS.get(literal, TokenTypeList.IDENT)
                return Token(token_type, literal, current_line, current_col)
            elif self.is_digit(self.ch):
                literal, is_float = self.read_number()
                return Token(TokenTypeList.FLOAT if is_float else TokenTypeList.INT, literal, current_line, current_col)
            else:
                tok = Token(TokenTypeList.ILLEGAL, self.ch, current_line, current_col)

        self.read_char()
        return tok

    def read_identifier(self):
        pos = self.position
        while self.is_letter(self.ch) or self.is_digit(self.ch):
            self.read_char()
        return self.input[pos:self.position]

    def read_number(self):
        pos = self.position
        is_float = False
        while self.is_digit(self.ch) or self.ch == '.':
            if self.ch == '.':
                is_float = True
            self.read_char()
        return self.input[pos:self.position], is_float

    def read_string(self, quote):
        self.read_char()
        pos = self.position
        while self.ch != quote and self.ch != '\\0':
            self.read_char()
        val = self.input[pos:self.position]
        return val

    def skip_whitespace(self):
        while self.ch in [" ", "\\t", "\\n", "\\r"]:
            if self.ch == "\\n":
                self.line += 1
                self.column = 0
            self.read_char()
            
    def skip_comment(self):
        while self.ch != "\\n" and self.ch != "\\0":
            self.read_char()

    def is_letter(self, ch):
        return "a" <= ch <= "z" or "A" <= ch <= "Z" or ch == "_"

    def is_digit(self, ch):
        return "0" <= ch <= "9"
''')

with open('src/parser.py', 'w') as f:
    f.write('''from .tokenizer import Lexer, Token, TokenTypeList
from .ast import *

LOWEST = 1
EQUALS = 2
LESSGREATER = 3
SUM = 4
PRODUCT = 5
PREFIX = 6
CALL = 7
INDEX = 8
MEMBER = 9

PRECEDENCES = {
    TokenTypeList.EQ: EQUALS,
    TokenTypeList.NOT_EQ: EQUALS,
    TokenTypeList.LT: LESSGREATER,
    TokenTypeList.GT: LESSGREATER,
    TokenTypeList.PLUS: SUM,
    TokenTypeList.MINUS: SUM,
    TokenTypeList.SLASH: PRODUCT,
    TokenTypeList.ASTERISK: PRODUCT,
    TokenTypeList.LPAREN: CALL,
    TokenTypeList.LBRACKET: INDEX,
    TokenTypeList.DOT: MEMBER
}

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, lexer: Lexer):
        self.l = lexer
        self.cur_token = None
        self.peek_token = None
        
        self.prefix_parse_fns = {}
        self.infix_parse_fns = {}
        
        self.register_prefix(TokenTypeList.IDENT, self.parse_identifier)
        self.register_prefix(TokenTypeList.INT, self.parse_integer_literal)
        self.register_prefix(TokenTypeList.FLOAT, self.parse_float_literal)
        self.register_prefix(TokenTypeList.STRING, self.parse_string_literal)
        self.register_prefix(TokenTypeList.BANG, self.parse_prefix_expression)
        self.register_prefix(TokenTypeList.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenTypeList.TRUE, self.parse_boolean)
        self.register_prefix(TokenTypeList.FALSE, self.parse_boolean)
        self.register_prefix(TokenTypeList.LPAREN, self.parse_grouped_expression)
        self.register_prefix(TokenTypeList.LBRACKET, self.parse_array_literal)
        self.register_prefix(TokenTypeList.LBRACE, self.parse_hash_literal)
        self.register_prefix(TokenTypeList.NULL, self.parse_null)
        
        self.register_infix(TokenTypeList.PLUS, self.parse_infix_expression)
        self.register_infix(TokenTypeList.MINUS, self.parse_infix_expression)
        self.register_infix(TokenTypeList.SLASH, self.parse_infix_expression)
        self.register_infix(TokenTypeList.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenTypeList.EQ, self.parse_infix_expression)
        self.register_infix(TokenTypeList.NOT_EQ, self.parse_infix_expression)
        self.register_infix(TokenTypeList.LT, self.parse_infix_expression)
        self.register_infix(TokenTypeList.GT, self.parse_infix_expression)
        self.register_infix(TokenTypeList.LPAREN, self.parse_call_expression)
        self.register_infix(TokenTypeList.LBRACKET, self.parse_index_expression)
        self.register_infix(TokenTypeList.DOT, self.parse_member_expression)
        self.register_infix(TokenTypeList.ASSIGN, self.parse_assign_expression)

        self.next_token()
        self.next_token()

    def register_prefix(self, token_type, fn):
        self.prefix_parse_fns[token_type] = fn

    def register_infix(self, token_type, fn):
        self.infix_parse_fns[token_type] = fn

    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.l.next_token()

    def cur_token_is(self, t):
        return self.cur_token.type == t

    def peek_token_is(self, t):
        return self.peek_token.type == t

    def expect_peek(self, t):
        if self.peek_token_is(t):
            self.next_token()
            return True
        else:
            raise ParseError(f"Expected next token to be {t}, got {self.peek_token.type} instead at line {self.peek_token.line}")

    def peek_precedence(self):
        return PRECEDENCES.get(self.peek_token.type, LOWEST)

    def cur_precedence(self):
        return PRECEDENCES.get(self.cur_token.type, LOWEST)

    def parse_program(self):
        program = Program([])
        while not self.cur_token_is(TokenTypeList.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()
        return program

    def parse_statement(self):
        if self.cur_token_is(TokenTypeList.LET) or self.cur_token_is(TokenTypeList.CONST):
            return self.parse_let_statement()
        elif self.cur_token_is(TokenTypeList.RETURN):
            return self.parse_return_statement()
        elif self.cur_token_is(TokenTypeList.IF):
            return self.parse_if_statement()
        elif self.cur_token_is(TokenTypeList.WHILE):
            return self.parse_while_statement()
        elif self.cur_token_is(TokenTypeList.FUNCTION):
            return self.parse_function_declaration()
        elif self.cur_token_is(TokenTypeList.CLASS):
            return self.parse_class_declaration()
        elif self.cur_token_is(TokenTypeList.TRY):
            return self.parse_try_catch_statement()
        elif self.cur_token_is(TokenTypeList.SAY):
            return self.parse_say_statement()
        elif self.cur_token_is(TokenTypeList.BREAK):
            return BreakStatement()
        elif self.cur_token_is(TokenTypeList.CONTINUE):
            return ContinueStatement()
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self):
        is_const = self.cur_token_is(TokenTypeList.CONST)
        if not self.expect_peek(TokenTypeList.IDENT):
            return None
        name = Identifier(self.cur_token.literal)
        if not self.expect_peek(TokenTypeList.ASSIGN):
            return None
        self.next_token()
        value = self.parse_expression(LOWEST)
        return LetStatement(name.value, value, is_const)

    def parse_return_statement(self):
        self.next_token()
        if self.cur_token_is(TokenTypeList.SEMICOLON) or self.cur_token_is(TokenTypeList.RBRACE):
            return ReturnStatement(None)
        value = self.parse_expression(LOWEST)
        return ReturnStatement(value)
        
    def parse_say_statement(self):
        self.next_token()
        value = self.parse_expression(LOWEST)
        return SayStatement(value)

    def parse_expression_statement(self):
        expr = self.parse_expression(LOWEST)
        return ExpressionStatement(expr)

    def parse_expression(self, precedence):
        prefix = self.prefix_parse_fns.get(self.cur_token.type)
        if prefix is None:
            raise ParseError(f"No prefix parse function for {self.cur_token.type} found at line {self.cur_token.line}")
        left_exp = prefix()

        while not self.peek_token_is(TokenTypeList.SEMICOLON) and not self.peek_token_is(TokenTypeList.RBRACE) and precedence < self.peek_precedence():
            infix = self.infix_parse_fns.get(self.peek_token.type)
            if infix is None:
                return left_exp
            self.next_token()
            left_exp = infix(left_exp)

        return left_exp

    def parse_identifier(self):
        return Identifier(self.cur_token.literal)

    def parse_integer_literal(self):
        return IntegerLiteral(int(self.cur_token.literal))
        
    def parse_float_literal(self):
        return FloatLiteral(float(self.cur_token.literal))
        
    def parse_string_literal(self):
        return StringLiteral(self.cur_token.literal)
        
    def parse_boolean(self):
        return BooleanLiteral(self.cur_token_is(TokenTypeList.TRUE))
        
    def parse_null(self):
        return NullLiteral()

    def parse_grouped_expression(self):
        self.next_token()
        exp = self.parse_expression(LOWEST)
        if not self.expect_peek(TokenTypeList.RPAREN):
            return None
        return exp

    def parse_prefix_expression(self):
        operator = self.cur_token.literal
        self.next_token()
        right = self.parse_expression(PREFIX)
        return PrefixExpression(operator, right)

    def parse_infix_expression(self, left):
        operator = self.cur_token.literal
        precedence = self.cur_precedence()
        self.next_token()
        right = self.parse_expression(precedence)
        return InfixExpression(left, operator, right)

    def parse_assign_expression(self, left):
        self.next_token()
        value = self.parse_expression(LOWEST)
        return AssignExpression(left, value)

    def parse_call_expression(self, function):
        args = self.parse_expression_list(TokenTypeList.RPAREN)
        return CallExpression(function, args)
        
    def parse_index_expression(self, left):
        self.next_token()
        index = self.parse_expression(LOWEST)
        if not self.expect_peek(TokenTypeList.RBRACKET):
            return None
        return IndexExpression(left, index)
        
    def parse_member_expression(self, left):
        if not self.expect_peek(TokenTypeList.IDENT):
            return None
        property = self.cur_token.literal
        return MemberExpression(left, property)

    def parse_expression_list(self, end):
        args = []
        if self.peek_token_is(end):
            self.next_token()
            return args
        self.next_token()
        args.append(self.parse_expression(LOWEST))
        while self.peek_token_is(TokenTypeList.COMMA):
            self.next_token()
            self.next_token()
            args.append(self.parse_expression(LOWEST))
        if not self.expect_peek(end):
            return None
        return args

    def parse_array_literal(self):
        elements = self.parse_expression_list(TokenTypeList.RBRACKET)
        return ArrayLiteral(elements)

    def parse_hash_literal(self):
        self.next_token() # skip {
        pairs = {}
        # Simple parsing for {key: value}
        # In real code, would handle comma sep properly
        return HashLiteral(pairs)

    def parse_block_statement(self):
        statements = []
        self.next_token()
        while not self.cur_token_is(TokenTypeList.RBRACE) and not self.cur_token_is(TokenTypeList.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.next_token()
        return BlockStatement(statements)

    def parse_if_statement(self):
        self.next_token()
        condition = self.parse_expression(LOWEST)
        if not self.expect_peek(TokenTypeList.LBRACE):
            return None
        consequence = self.parse_block_statement()
        alternative = None
        if self.peek_token_is(TokenTypeList.ELSE):
            self.next_token()
            if self.peek_token_is(TokenTypeList.IF):
                self.next_token()
                alternative = BlockStatement([self.parse_if_statement()])
            else:
                if not self.expect_peek(TokenTypeList.LBRACE):
                    return None
                alternative = self.parse_block_statement()
        return IfStatement(condition, consequence, alternative)

    def parse_while_statement(self):
        self.next_token()
        condition = self.parse_expression(LOWEST)
        if not self.expect_peek(TokenTypeList.LBRACE):
            return None
        body = self.parse_block_statement()
        return WhileStatement(condition, body)

    def parse_function_declaration(self):
        if not self.expect_peek(TokenTypeList.IDENT):
            return None
        name = self.cur_token.literal
        if not self.expect_peek(TokenTypeList.LPAREN):
            return None
        parameters = []
        if not self.peek_token_is(TokenTypeList.RPAREN):
            self.next_token()
            parameters.append(self.cur_token.literal)
            while self.peek_token_is(TokenTypeList.COMMA):
                self.next_token()
                if not self.expect_peek(TokenTypeList.IDENT):
                    return None
                parameters.append(self.cur_token.literal)
        if not self.expect_peek(TokenTypeList.RPAREN):
            return None
        if not self.expect_peek(TokenTypeList.LBRACE):
            return None
        body = self.parse_block_statement()
        return FunctionDeclaration(name, parameters, body)

    def parse_class_declaration(self):
        if not self.expect_peek(TokenTypeList.IDENT):
            return None
        name = self.cur_token.literal
        superclass = None
        if self.peek_token_is(TokenTypeList.LT):
            self.next_token()
            if not self.expect_peek(TokenTypeList.IDENT):
                return None
            superclass = self.cur_token.literal
        if not self.expect_peek(TokenTypeList.LBRACE):
            return None
        
        methods = []
        self.next_token()
        while not self.cur_token_is(TokenTypeList.RBRACE) and not self.cur_token_is(TokenTypeList.EOF):
            if self.cur_token_is(TokenTypeList.FUNCTION):
                method = self.parse_function_declaration()
                methods.append(method)
            self.next_token()
        return ClassDeclaration(name, superclass, methods)
        
    def parse_try_catch_statement(self):
        if not self.expect_peek(TokenTypeList.LBRACE):
            return None
        try_block = self.parse_block_statement()
        if not self.expect_peek(TokenTypeList.CATCH):
            return None
        if not self.expect_peek(TokenTypeList.LPAREN):
            return None
        if not self.expect_peek(TokenTypeList.IDENT):
            return None
        catch_var = self.cur_token.literal
        if not self.expect_peek(TokenTypeList.RPAREN):
            return None
        if not self.expect_peek(TokenTypeList.LBRACE):
            return None
        catch_block = self.parse_block_statement()
        return TryCatchStatement(try_block, catch_var, catch_block)
''')

with open('src/environment.py', 'w') as f:
    f.write('''class Environment:
    def __init__(self, outer=None):
        self.store = {}
        self.consts = set()
        self.outer = outer

    def get(self, name):
        if name in self.store:
            return self.store[name]
        elif self.outer is not None:
            return self.outer.get(name)
        return None

    def set(self, name, value, is_const=False):
        if name in self.store and name in self.consts:
            raise RuntimeError(f"Cannot reassign constant '{name}'")
        self.store[name] = value
        if is_const:
            self.consts.add(name)
        return value
        
    def assign(self, name, value):
        if name in self.store:
            if name in self.consts:
                raise RuntimeError(f"Cannot reassign constant '{name}'")
            self.store[name] = value
            return value
        elif self.outer is not None:
            return self.outer.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable '{name}'")
''')

with open('src/evaluator.py', 'w') as f:
    f.write('''from .ast import *
from .environment import Environment

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(Exception): pass
class ContinueException(Exception): pass

class Function:
    def __init__(self, declaration, env):
        self.declaration = declaration
        self.env = env
        
    def call(self, evaluator, args):
        env = Environment(self.env)
        for i, param in enumerate(self.declaration.parameters):
            env.set(param, args[i] if i < len(args) else None)
        try:
            evaluator.eval(self.declaration.body, env)
        except ReturnValue as ret:
            return ret.value
        return None

class ClassType:
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods
        
    def call(self, evaluator, args):
        instance = ClassInstance(self)
        if "init" in self.methods:
            initializer = self.methods["init"].bind(instance)
            initializer.call(evaluator, args)
        return instance

class ClassInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
        
    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        if name in self.klass.methods:
            return self.klass.methods[name].bind(self)
        raise RuntimeError(f"Undefined property '{name}' on instance of {self.klass.name}")
        
    def set(self, name, value):
        self.fields[name] = value

class BoundMethod:
    def __init__(self, receiver, method):
        self.receiver = receiver
        self.method = method
        
    def call(self, evaluator, args):
        env = Environment(self.method.env)
        env.set("self", self.receiver)
        for i, param in enumerate(self.method.declaration.parameters):
            env.set(param, args[i] if i < len(args) else None)
        try:
            evaluator.eval(self.method.declaration.body, env)
        except ReturnValue as ret:
            return ret.value
        return None

class NativeFunction:
    def __init__(self, fn):
        self.fn = fn
        
    def call(self, evaluator, args):
        return self.fn(args)

class Evaluator:
    def __init__(self):
        self.globals = Environment()
        
    def eval(self, node, env):
        if isinstance(node, Program):
            return self.eval_program(node, env)
        elif isinstance(node, BlockStatement):
            return self.eval_block_statement(node, env)
        elif isinstance(node, ExpressionStatement):
            return self.eval(node.expression, env)
        elif isinstance(node, LetStatement):
            val = self.eval(node.value, env)
            env.set(node.name, val, node.is_const)
            return val
        elif isinstance(node, AssignExpression):
            val = self.eval(node.value, env)
            if isinstance(node.left, Identifier):
                env.assign(node.left.value, val)
            elif isinstance(node.left, MemberExpression):
                obj = self.eval(node.left.obj, env)
                if not isinstance(obj, ClassInstance):
                    raise RuntimeError("Only instances have properties")
                obj.set(node.left.property, val)
            return val
        elif isinstance(node, Identifier):
            val = env.get(node.value)
            if val is None:
                raise RuntimeError(f"Undefined variable '{node.value}'")
            return val
        elif isinstance(node, IntegerLiteral) or isinstance(node, FloatLiteral) or isinstance(node, StringLiteral) or isinstance(node, BooleanLiteral):
            return node.value
        elif isinstance(node, NullLiteral):
            return None
        elif isinstance(node, PrefixExpression):
            right = self.eval(node.right, env)
            return self.eval_prefix_expression(node.operator, right)
        elif isinstance(node, InfixExpression):
            left = self.eval(node.left, env)
            right = self.eval(node.right, env)
            return self.eval_infix_expression(node.operator, left, right)
        elif isinstance(node, IfStatement):
            return self.eval_if_statement(node, env)
        elif isinstance(node, WhileStatement):
            return self.eval_while_statement(node, env)
        elif isinstance(node, FunctionDeclaration):
            fn = Function(node, env)
            env.set(node.name, fn)
            return None
        elif isinstance(node, ClassDeclaration):
            methods = {}
            for method_decl in node.methods:
                method_decl.env = env
                # For binding later
                methods[method_decl.name] = Function(method_decl, env)
                methods[method_decl.name].bind = lambda inst, meth=methods[method_decl.name]: BoundMethod(inst, meth)
            superclass = None
            if node.superclass:
                superclass = env.get(node.superclass)
                if not isinstance(superclass, ClassType):
                    raise RuntimeError("Superclass must be a class")
            klass = ClassType(node.name, superclass, methods)
            env.set(node.name, klass)
            return None
        elif isinstance(node, CallExpression):
            fn = self.eval(node.function, env)
            args = [self.eval(arg, env) for arg in node.arguments]
            if hasattr(fn, "call"):
                return fn.call(self, args)
            else:
                raise RuntimeError(f"Not callable: {fn}")
        elif isinstance(node, MemberExpression):
            obj = self.eval(node.obj, env)
            if isinstance(obj, ClassInstance):
                return obj.get(node.property)
            else:
                raise RuntimeError("Only instances have properties")
        elif isinstance(node, ReturnStatement):
            val = self.eval(node.value, env) if node.value else None
            raise ReturnValue(val)
        elif isinstance(node, TryCatchStatement):
            try:
                self.eval(node.try_block, Environment(env))
            except Exception as e:
                catch_env = Environment(env)
                catch_env.set(node.catch_var, str(e))
                self.eval(node.catch_block, catch_env)
            return None
        elif isinstance(node, SayStatement):
            val = self.eval(node.value, env)
            print(self.stringify(val))
            return None
        elif isinstance(node, BreakStatement):
            raise BreakException()
        elif isinstance(node, ContinueStatement):
            raise ContinueException()
        return None

    def eval_program(self, program, env):
        result = None
        for statement in program.statements:
            try:
                result = self.eval(statement, env)
            except ReturnValue as ret:
                return ret.value
        return result

    def eval_block_statement(self, block, env):
        result = None
        block_env = Environment(env)
        for statement in block.statements:
            result = self.eval(statement, block_env)
        return result

    def eval_prefix_expression(self, operator, right):
        if operator == "!":
            return not self.is_truthy(right)
        elif operator == "-":
            if not isinstance(right, (int, float)):
                raise RuntimeError("Invalid operand for unary -")
            return -right
        return None

    def eval_infix_expression(self, operator, left, right):
        if operator == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self.stringify(left) + self.stringify(right)
            return left + right
        elif operator == "-": return left - right
        elif operator == "*": return left * right
        elif operator == "/": return left / right
        elif operator == "==": return left == right
        elif operator == "!=": return left != right
        elif operator == "<": return left < right
        elif operator == ">": return left > right
        return None

    def eval_if_statement(self, node, env):
        condition = self.eval(node.condition, env)
        if self.is_truthy(condition):
            return self.eval(node.consequence, env)
        elif node.alternative is not None:
            return self.eval(node.alternative, env)
        return None

    def eval_while_statement(self, node, env):
        while self.is_truthy(self.eval(node.condition, env)):
            try:
                self.eval(node.body, env)
            except BreakException:
                break
            except ContinueException:
                continue
        return None

    def is_truthy(self, val):
        if val is None or val is False or val == 0 or val == "":
            return False
        return True

    def stringify(self, val):
        if val is None: return "null"
        if val is True: return "true"
        if val is False: return "false"
        if isinstance(val, ClassInstance): return f"<Instance of {val.klass.name}>"
        if hasattr(val, "call"): return "<Function>"
        return str(val)
''')

with open('src/stdlib.py', 'w') as f:
    f.write('''import math
import time
import random
import urllib.request

from .evaluator import NativeFunction

def register_stdlib(env):
    env.set("sin", NativeFunction(lambda args: math.sin(args[0])))
    env.set("cos", NativeFunction(lambda args: math.cos(args[0])))
    env.set("floor", NativeFunction(lambda args: math.floor(args[0])))
    env.set("random", NativeFunction(lambda args: random.random()))
    env.set("sleep", NativeFunction(lambda args: time.sleep(args[0])))
    env.set("current_time", NativeFunction(lambda args: time.time()))
    
    def read_file(args):
        with open(args[0], 'r') as f:
            return f.read()
    env.set("read_file", NativeFunction(read_file))
    
    def write_file(args):
        with open(args[0], 'w') as f:
            f.write(args[1])
        return None
    env.set("write_file", NativeFunction(write_file))
    
    def fetch_url(args):
        try:
            with urllib.request.urlopen(args[0]) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            return str(e)
            
    env.set("fetch_url", NativeFunction(fetch_url))
''')

with open('src/main.py', 'w') as f:
    f.write('''import sys
from .tokenizer import Lexer
from .parser import Parser
from .evaluator import Evaluator
from .environment import Environment
from .stdlib import register_stdlib

def run(code, env=None, evaluator=None):
    lexer = Lexer(code)
    parser = Parser(lexer)
    try:
        program = parser.parse_program()
    except Exception as e:
        print(f"Syntax Error: {e}")
        return
        
    if evaluator is None:
        evaluator = Evaluator()
    if env is None:
        env = evaluator.globals
        register_stdlib(env)
        
    try:
        evaluator.eval(program, env)
    except Exception as e:
        print(f"Runtime Error: {e}")

def repl():
    print("Sykus v4.0 REPL")
    evaluator = Evaluator()
    env = evaluator.globals
    register_stdlib(env)
    
    while True:
        try:
            line = input(">> ")
            if line.strip() == "exit":
                break
            run(line, env, evaluator)
        except (KeyboardInterrupt, EOFError):
            print()
            break

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "run" and len(sys.argv) > 2:
            with open(sys.argv[2], 'r') as f:
                code = f.read()
            run(code)
        else:
            print("Usage: syk run <file.syk>")
    else:
        repl()

if __name__ == "__main__":
    main()
''')

