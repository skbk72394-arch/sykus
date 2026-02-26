import re
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
    IMPORT = "IMPORT"

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
    "continue": TokenTypeList.CONTINUE,
    "import": TokenTypeList.IMPORT
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
            self.ch = '\0'
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1
        self.column += 1

    def peek_char(self):
        if self.read_position >= len(self.input):
            return '\0'
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
        elif self.ch == '"' or self.ch == "'":
            tok = Token(TokenTypeList.STRING, self.read_string(self.ch), current_line, current_col)
        elif self.ch == '\0':
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
        while self.ch != quote and self.ch != '\0':
            self.read_char()
        val = self.input[pos:self.position]
        return val

    def skip_whitespace(self):
        while self.ch in [" ", "\t", "\n", "\r"]:
            if self.ch == "\n":
                self.line += 1
                self.column = 0
            self.read_char()
            
    def skip_comment(self):
        while self.ch != "\n" and self.ch != "\0":
            self.read_char()

    def is_letter(self, ch):
        return "a" <= ch <= "z" or "A" <= ch <= "Z" or ch == "_"

    def is_digit(self, ch):
        return "0" <= ch <= "9"