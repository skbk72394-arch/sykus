from lexer import Lexer, Token, TokenTypeList
from syk_ast import *

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
    TokenTypeList.LTE: LESSGREATER,
    TokenTypeList.GTE: LESSGREATER,
    TokenTypeList.PLUS: SUM,
    TokenTypeList.MINUS: SUM,
    TokenTypeList.SLASH: PRODUCT,
    TokenTypeList.ASTERISK: PRODUCT,
    TokenTypeList.LPAREN: CALL,
    TokenTypeList.LBRACKET: INDEX,
    TokenTypeList.DOT: MEMBER
}

class ParseError(Exception):
    def __init__(self, message, line=None, column=None):
        super().__init__(message)
        self.line = line
        self.column = column

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
        self.register_infix(TokenTypeList.LTE, self.parse_infix_expression)
        self.register_infix(TokenTypeList.GTE, self.parse_infix_expression)
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
            raise ParseError(
                f"Expected next token to be {t}, got {self.peek_token.type} instead",
                line=self.peek_token.line,
                column=self.peek_token.column
            )

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
        elif self.cur_token_is(TokenTypeList.FOR):
            return self.parse_for_statement()
        elif self.cur_token_is(TokenTypeList.FUNCTION):
            return self.parse_function_declaration()
        elif self.cur_token_is(TokenTypeList.CLASS):
            return self.parse_class_declaration()
        elif self.cur_token_is(TokenTypeList.TRY):
            return self.parse_try_catch_statement()
        elif self.cur_token_is(TokenTypeList.SAY):
            return self.parse_say_statement()
        elif self.cur_token_is(TokenTypeList.ASK):
            return self.parse_ask_statement()
        elif self.cur_token_is(TokenTypeList.BREAK):
            return BreakStatement()
        elif self.cur_token_is(TokenTypeList.CONTINUE):
            return ContinueStatement()
        elif self.cur_token_is(TokenTypeList.IMPORT):
            return self.parse_import_statement()
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
        if self.peek_token_is(TokenTypeList.SEMICOLON):
            self.next_token()
        return LetStatement(name.value, value, is_const)

    def parse_return_statement(self):
        self.next_token()
        if self.cur_token_is(TokenTypeList.SEMICOLON) or self.cur_token_is(TokenTypeList.RBRACE):
            return ReturnStatement(None)
        value = self.parse_expression(LOWEST)
        if self.peek_token_is(TokenTypeList.SEMICOLON):
            self.next_token()
        return ReturnStatement(value)
        
    def parse_say_statement(self):
        self.next_token()
        value = self.parse_expression(LOWEST)
        if self.peek_token_is(TokenTypeList.SEMICOLON):
            self.next_token()
        return SayStatement(value)

    def parse_ask_statement(self):
        self.next_token() # consume 'ask'
        prompt = self.parse_expression(LOWEST)
        if not self.expect_peek(TokenTypeList.SAVE):
            return None
        if not self.expect_peek(TokenTypeList.TO):
            return None
        if not self.expect_peek(TokenTypeList.IDENT):
            return None
        name = self.cur_token.literal
        if self.peek_token_is(TokenTypeList.SEMICOLON):
            self.next_token()
        return AskStatement(prompt, name)

    def parse_import_statement(self):
        self.next_token()
        file_path = self.parse_expression(LOWEST)
        if self.peek_token_is(TokenTypeList.SEMICOLON):
            self.next_token()
        return ImportStatement(file_path)

    def parse_expression_statement(self):
        expr = self.parse_expression(LOWEST)
        if self.peek_token_is(TokenTypeList.SEMICOLON):
            self.next_token()
        return ExpressionStatement(expr)

    def parse_expression(self, precedence):
        prefix = self.prefix_parse_fns.get(self.cur_token.type)
        if prefix is None:
            raise ParseError(
                f"No prefix parse function for {self.cur_token.type} found",
                line=self.cur_token.line,
                column=self.cur_token.column
            )
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
        self.next_token()
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
        pairs = []
        while not self.cur_token_is(TokenTypeList.RBRACE) and not self.cur_token_is(TokenTypeList.EOF):
            key = self.parse_expression(LOWEST)
            if not self.expect_peek(TokenTypeList.COLON):
                return None
            self.next_token()
            value = self.parse_expression(LOWEST)
            pairs.append((key, value))
            if not self.peek_token_is(TokenTypeList.RBRACE) and not self.expect_peek(TokenTypeList.COMMA):
                return None
            self.next_token()
        if not self.cur_token_is(TokenTypeList.RBRACE):
            raise ParseError("Expected }", line=self.cur_token.line, column=self.cur_token.column)
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

    def parse_for_statement(self):
        self.next_token()
        init = None
        if not self.cur_token_is(TokenTypeList.SEMICOLON):
            init = self.parse_statement()
        else:
            self.next_token()
            
        condition = None
        if not self.cur_token_is(TokenTypeList.SEMICOLON):
            condition = self.parse_expression(LOWEST)
            self.next_token()
        else:
            self.next_token()
            
        update = None
        if not self.cur_token_is(TokenTypeList.LBRACE):
            update = self.parse_statement()
            
        if not self.cur_token_is(TokenTypeList.LBRACE) and not self.expect_peek(TokenTypeList.LBRACE):
            return None
            
        body = self.parse_block_statement()
        return ForStatement(init, condition, update, body)

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
