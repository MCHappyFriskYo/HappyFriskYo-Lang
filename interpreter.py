# interpreter.py
from parser import Num, Str, Var, BinOp, Compare, Assign, Print, While, Block

class Interpreter:
    def __init__(self):
        self.env = {}

    def eval(self, node):
        if isinstance(node, Num):
            return node.value

        elif isinstance(node, Str):          # 新增：返回字符串值
            return node.value

        elif isinstance(node, Var):
            if node.name not in self.env:
                raise NameError(f"Variable '{node.name}' is not defined")
            return self.env[node.name]

        elif isinstance(node, BinOp):
            left_val = self.eval(node.left)
            right_val = self.eval(node.right)
            # 检查类型，只支持数字运算
            if not isinstance(left_val, (int, float)) or not isinstance(right_val, (int, float)):
                raise TypeError(f"Operator '{node.op}' requires numbers, got {type(left_val).__name__} and {type(right_val).__name__}")
            if node.op == '+':
                return left_val + right_val
            elif node.op == '-':
                return left_val - right_val
            elif node.op == '*':
                return left_val * right_val
            elif node.op == '/':
                if right_val == 0:
                    raise ZeroDivisionError("Division by zero")
                return left_val / right_val
            else:
                raise NotImplementedError(f"Operator '{node.op}' not supported")

        elif isinstance(node, Compare):
            left_val = self.eval(node.left)
            right_val = self.eval(node.right)
            # 比较运算符支持数字和字符串（但字符串只支持 == 和 != 比较合理）
            # 这里简单允许任意类型比较
            if node.op == '<':
                return left_val < right_val
            elif node.op == '>':
                return left_val > right_val
            elif node.op == '==':
                return left_val == right_val
            elif node.op == '!=':
                return left_val != right_val
            elif node.op == '<=':
                return left_val <= right_val
            elif node.op == '>=':
                return left_val >= right_val
            else:
                raise NotImplementedError(f"Comparison '{node.op}' not supported")

        elif isinstance(node, Assign):
            val = self.eval(node.expr)
            self.env[node.var.name] = val
            return val

        elif isinstance(node, Print):
            val = self.eval(node.expr)
            return val          # 返回给主程序输出

        elif isinstance(node, While):
            while True:
                cond_val = self.eval(node.condition)
                if not cond_val:
                    break
                self.eval(node.body)
            return None

        elif isinstance(node, Block):
            result = None
            for stmt in node.statements:
                result = self.eval(stmt)
            return result

        else:
            raise NotImplementedError(f"Unknown AST node type: {type(node)}")