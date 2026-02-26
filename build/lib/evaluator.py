from syk_ast import *
from environment import Environment

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
            try:
                env.set(node.name, val, node.is_const)
            except RuntimeError:
                env.store[node.name] = val
            return val
        elif isinstance(node, AssignExpression):
            val = self.eval(node.value, env)
            if isinstance(node.left, Identifier):
                env.assign(node.left.value, val)
            elif isinstance(node.left, MemberExpression):
                obj = self.eval(node.left.obj, env)
                if isinstance(obj, ClassInstance):
                    obj.set(node.left.property, val)
                elif isinstance(obj, dict):
                    obj[node.left.property] = val
                else:
                    raise RuntimeError("Only instances or dictionaries have properties")
            elif isinstance(node.left, IndexExpression):
                left_val = self.eval(node.left.left, env)
                idx = self.eval(node.left.index, env)
                if isinstance(left_val, list):
                    left_val[idx] = val
                elif isinstance(left_val, dict):
                    left_val[idx] = val
                else:
                    raise RuntimeError("Index assignment not supported")
            return val
        elif isinstance(node, Identifier):
            val = env.get(node.value)
            if val is None:
                raise RuntimeError(f"Undefined variable '{node.value}'")
            return val
        elif isinstance(node, IntegerLiteral) or isinstance(node, FloatLiteral) or isinstance(node, BooleanLiteral):
            return node.value
        elif isinstance(node, StringLiteral):
            val = node.value
            import re
            def replace_var(match):
                var_name = match.group(1)
                try:
                    var_val = env.get(var_name)
                    return self.stringify(var_val)
                except RuntimeError:
                    return match.group(0)
            return re.sub(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', replace_var, val)
        elif isinstance(node, NullLiteral):
            return None
        elif isinstance(node, ArrayLiteral):
            return [self.eval(e, env) for e in node.elements]
        elif isinstance(node, HashLiteral):
            pairs = {}
            for k_node, v_node in node.pairs:
                key = self.eval(k_node, env)
                value = self.eval(v_node, env)
                pairs[key] = value
            return pairs
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
        elif isinstance(node, ForStatement):
            if node.init:
                self.eval(node.init, env)
            while True:
                if node.condition:
                    cond = self.eval(node.condition, env)
                    if not self.is_truthy(cond):
                        break
                try:
                    self.eval(node.body, env)
                except BreakException:
                    break
                except ContinueException:
                    if node.update:
                        self.eval(node.update, env)
                    continue
                if node.update:
                    self.eval(node.update, env)
            return None
        elif isinstance(node, FunctionDeclaration):
            fn = Function(node, env)
            env.store[node.name] = fn
            return None
        elif isinstance(node, ClassDeclaration):
            methods = {}
            for method_decl in node.methods:
                method_decl.env = env
                methods[method_decl.name] = Function(method_decl, env)
                methods[method_decl.name].bind = lambda inst, meth=methods[method_decl.name]: BoundMethod(inst, meth)
            superclass = None
            if node.superclass:
                superclass = env.get(node.superclass)
                if not isinstance(superclass, ClassType):
                    raise RuntimeError("Superclass must be a class")
            klass = ClassType(node.name, superclass, methods)
            env.store[node.name] = klass
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
            elif isinstance(obj, dict):
                return obj.get(node.property)
            else:
                raise RuntimeError(f"Property access not supported on {type(obj)}")
        elif isinstance(node, IndexExpression):
            left = self.eval(node.left, env)
            index = self.eval(node.index, env)
            if isinstance(left, list) and isinstance(index, int):
                return left[index]
            elif isinstance(left, dict):
                return left.get(index)
            raise RuntimeError(f"Index access not supported on {type(left)} with index {type(index)}")
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
        elif isinstance(node, ImportStatement):
            file_path = self.eval(node.file_path, env)
            if not isinstance(file_path, str):
                raise RuntimeError("Import path must be a string")
            import os
            if not os.path.exists(file_path):
                raise RuntimeError(f"Cannot import '{file_path}': File not found")
            with open(file_path, 'r') as f:
                code = f.read()
            from lexer import Lexer
            from parser import Parser
            lexer = Lexer(code)
            parser = Parser(lexer)
            program = parser.parse_program()
            self.eval_program(program, env)
            return None
        elif isinstance(node, SayStatement):
            val = self.eval(node.value, env)
            print(self.stringify(val))
            return None
        elif isinstance(node, AskStatement):
            prompt = self.eval(node.prompt, env)
            val = input(self.stringify(prompt))
            env.store[node.name] = val
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
        elif operator == ">=": return left >= right
        elif operator == "<=": return left <= right
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
        if isinstance(val, dict) and 'run' in val: return "<Namespace>"
        if isinstance(val, list): return "[" + ", ".join([self.stringify(x) for x in val]) + "]"
        if isinstance(val, dict): return "{" + ", ".join([f'"{k}": {self.stringify(v)}' for k, v in val.items()]) + "}"
        return str(val)
