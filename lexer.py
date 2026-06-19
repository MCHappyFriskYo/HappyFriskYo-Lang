# lexer.py
import re

class TokenType:
    # 关键字
    PRINT = 'PRINT'
    WHILE = 'WHILE'
    DO = 'DO'
    END = 'END'
    
    # 标识符与数值
    ID = 'ID'
    NUM = 'NUM'
    STRING = 'STRING'          # 新增字符串类型
    
    # 运算符
    ASSIGN = 'ASSIGN'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    
    # 比较运算符
    LT = 'LT'
    GT = 'GT'
    EQ = 'EQ'
    NE = 'NE'
    LE = 'LE'
    GE = 'GE'
    
    # 括号
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    
    EOF = 'EOF'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.tokens = []

    def tokenize(self):
        rules = [
            (TokenType.WHILE, r'while\b'),
            (TokenType.DO,    r'do\b'),
            (TokenType.END,   r'end\b'),
            (TokenType.PRINT, r'print\b'),
            
            (TokenType.ID,    r'[a-zA-Z_][a-zA-Z0-9_]*'),
            (TokenType.NUM,   r'\d+'),
            (TokenType.STRING, r'"[^"]*"'),   # 新增：双引号字符串
            
            (TokenType.ASSIGN, r'='),
            
            (TokenType.GE,    r'>='),
            (TokenType.LE,    r'<='),
            (TokenType.NE,    r'!='),
            (TokenType.EQ,    r'=='),
            (TokenType.GT,    r'>'),
            (TokenType.LT,    r'<'),
            
            (TokenType.PLUS,  r'\+'),
            (TokenType.MINUS, r'-'),
            (TokenType.MUL,   r'\*'),
            (TokenType.DIV,   r'/'),
            
            (TokenType.LPAREN, r'\('),
            (TokenType.RPAREN, r'\)'),
        ]

        while self.pos < len(self.code):
            if self.code[self.pos].isspace():
                self.pos += 1
                continue

            matched = False
            for token_type, pattern in rules:
                regex = re.compile(pattern)
                match = regex.match(self.code, self.pos)
                if match:
                    value = match.group(0)
                    if token_type == TokenType.NUM:
                        value = int(value)
                    elif token_type == TokenType.STRING:
                        # 去掉两端的双引号，保留内容
                        value = value[1:-1]
                    self.tokens.append(Token(token_type, value))
                    self.pos = match.end()
                    matched = True
                    break

            if not matched:
                raise SyntaxError(f"Unknown character: '{self.code[self.pos]}' at position {self.pos}")

        self.tokens.append(Token(TokenType.EOF, None))
        return self.tokens