# parser.py
from lexer import TokenType

# ---------- AST 节点 ----------
class ASTNode:
    pass

class Num(ASTNode):
    def __init__(self, value):
        self.value = value

class Str(ASTNode):          # 新增字符串节点
    def __init__(self, value):
        self.value = value

class Var(ASTNode):
    def __init__(self, name):
        self.name = name

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Compare(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Assign(ASTNode):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

class Print(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

# ---------- 语法分析器 ----------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, expected_type=None):
        token = self.peek()
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, but got {token.type} (value: {token.value})")
        self.pos += 1
        return token

    def parse_program(self):
        stmts = []
        while self.peek().type != TokenType.EOF:
            stmts.append(self.parse_statement())
        return Block(stmts)

    def parse_statement(self):
        token = self.peek()
        if token.type == TokenType.WHILE:
            return self.parse_while()
        elif token.type == TokenType.PRINT:
            self.consume(TokenType.PRINT)
            expr = self.expr()
            return Print(expr)
        elif token.type == TokenType.ID:
            var_name = self.consume(TokenType.ID).value
            self.consume(TokenType.ASSIGN)
            expr = self.expr()
            return Assign(Var(var_name), expr)
        else:
            return self.expr()

    def parse_while(self):
        self.consume(TokenType.WHILE)
        condition = self.parse_comp()
        self.consume(TokenType.DO)
        body = self.parse_block()
        self.consume(TokenType.END)
        return While(condition, body)

    def parse_block(self):
        stmts = []
        while self.peek().type != TokenType.END and self.peek().type != TokenType.EOF:
            stmts.append(self.parse_statement())
        return Block(stmts)

    def parse_comp(self):
        node = self.expr()
        if self.peek().type in (TokenType.LT, TokenType.GT, TokenType.EQ, 
                                TokenType.NE, TokenType.LE, TokenType.GE):
            op_token = self.consume()
            right = self.expr()
            return Compare(node, op_token.value, right)
        return node

    def expr(self):
        node = self.term()
        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.consume()
            right = self.term()
            node = BinOp(node, op_token.value, right)
        return node

    def term(self):
        node = self.factor()
        while self.peek().type in (TokenType.MUL, TokenType.DIV):
            op_token = self.consume()
            right = self.factor()
            node = BinOp(node, op_token.value, right)
        return node

    def factor(self):
        token = self.peek()
        if token.type == TokenType.NUM:
            self.consume()
            return Num(token.value)
        elif token.type == TokenType.STRING:      # 新增：识别字符串
            self.consume()
            return Str(token.value)
        elif token.type == TokenType.ID:
            self.consume()
            return Var(token.name)
        elif token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            node = self.expr()
            self.consume(TokenType.RPAREN)
            return node
        else:
            raise SyntaxError(f"Expected number, string, variable or '(', but got {token.type}")