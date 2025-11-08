from typing import override

from callables.saga_callable import SAGACallable, SAGAFunction
from callables.native_callables import (
    ClockCallable,
    RandomCallable,
    RandomIntCallable,
    InputCallable,
    ReadFileCallable,
    WriteFileCallable,
    AppendFileCallable,
    FileExistsCallable,
    DeleteFileCallable
)
import expr.expr as expr
from expr.expr import Expr, Grouping, Binary, Unary, Ternary, Literal

import stmt.stmt as stmt
from stmt.stmt import Stmt, Expression, Say, Let, If, Break, Continue

from lexer.token_type import TokenType
from lexer.token import Token

from errors.errors import RuntimeError, Error, ContinueException, BreakException, ReturnException

from environment.environment import Environment

# TODO: Handle distinction between floats & integer in SAGA

class Interpreter(expr.Visitor, stmt.Visitor):

    def __init__(self):
        self.globals = Environment()
        self.env = self.globals
        self.locals = {}

        # define native functions
        self.globals.define("clock", ClockCallable())
        self.globals.define("random", RandomCallable())
        self.globals.define("random_int", RandomIntCallable())
        self.globals.define("input", InputCallable())
        self.globals.define("read_file", ReadFileCallable())
        self.globals.define("write_file", WriteFileCallable())
        self.globals.define("append_file", AppendFileCallable())
        self.globals.define("file_exists", FileExistsCallable())
        self.globals.define("delete_file", DeleteFileCallable())

    def interpret(self, statements: list[Stmt]):
        try:
            for stmt in statements:
                self.execute(stmt)
        except RuntimeError as error:
            Error.runtime_error(error)

    def execute(self, statement: Stmt):
        statement.accept(self)

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth

    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous: Environment = self.env
        try:
            self.env = environment

            for stmt in statements:
                self.execute(stmt)
        finally:
            self.env = previous

    @override
    def visit_block(self, block):
        self.execute_block(block.statements, Environment(self.env))
        return None

    @override
    def visit_literal(self, literal: Literal):
        return literal.value
    
    @override
    def visit_logical(self, expr):
        left: any = self.evaluate(expr.left)

        # Short-circuiting
        if expr.operator.type == TokenType.OR:
            if self.is_truthful(left): return left
        else:    
            if not self.is_truthful(left): return left
        
        return self.evaluate(expr.right)

    @override
    def visit_grouping(self, grouping: Grouping):
        return self.evaluate(grouping.expression)
    
    @override
    def visit_unary(self, unary: Unary):
        right: any = self.evaluate(unary.right)

        match unary.operator.type:
            case TokenType.MINUS:
                self.check_number_operand(unary.operator, right)
                return -right
            case TokenType.BANG:
                return not self.is_truthful(right)
        
        # unreachable
        return None

    @override
    def visit_binary(self, binary: Binary):
        left: any = self.evaluate(binary.left)
        right: any = self.evaluate(binary.right)

        match binary.operator.type:
            case TokenType.COMMA:
                left_values = left if isinstance(left, tuple) else (left,)
                right_values = right if isinstance(right, tuple) else (right,)
                return left_values + right_values
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.GREATER:
                self.check_number_operands(binary.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(binary.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self.check_number_operands(binary.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(binary.operator, left, right)
                return left <= right
            case TokenType.MINUS:
                self.check_number_operands(binary.operator, left, right)
                return left - right
            case TokenType.PLUS:
                # This operator is special because it can either be
                # addition or concatenation
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                elif (isinstance(left, (int, float)) and isinstance(right, str)) or (isinstance(left, str) and isinstance(right, (int, float))):
                    return str(left) + str(right)
                raise RuntimeError(binary.operator, 
                    "Operands must be two numbers or two strings.")
            case TokenType.SLASH:
                self.check_number_operands(binary.operator, left, right)
                if right != 0:
                    return left / right
                raise RuntimeError(binary.operator, "Cannot divide by zero.")
            case TokenType.STAR:
                self.check_number_operands(binary.operator, left, right)
                return left * right
        
        # unreachable
        return None
    
    @override
    def visit_call(self, expr):
        callee: any = self.evaluate(expr.callee)
        if not isinstance(callee, SAGACallable):
            raise RuntimeError(expr.paren, "Can only call functions or classes.")

        arguments: list[any] = []
        for arg in expr.arguments:
            arguments.append(self.evaluate(arg))
        
        function: SAGACallable = callee
        
        # Handle variadic functions (arity -1) differently
        if function.arity() != -1 and len(arguments) != function.arity():
            raise RuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")

        return function.call(self, arguments)
    
    @override
    def visit_ternary(self, ternary: Ternary):
        condition: any = self.evaluate(ternary.condition)
        
        if self.is_truthful(condition):
            return self.evaluate(ternary.then_branch)
        else:
            return self.evaluate(ternary.else_branch)

    @override
    def visit_variable(self, variable):
        return self.look_up_variable(variable.name, variable)

    def look_up_variable(self, name: Token, variable: Expr):
        distance: int = self.locals.get(variable)
        if distance is not None:
            return self.env.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    @override
    def visit_assign(self, assign):
        value: any = self.evaluate(assign.value)

        distance: int = self.locals.get(assign)
        if distance is not None:
            self.env.assign_at(distance, assign.name, value)
        else:
            self.globals.assign(assign.name, value)

        return value

    @override
    def visit_expression(self, expression):
        self.evaluate(expression.expression)
        return None

    @override
    def visit_function(self, stmt):
        # We pass the environment that is active when 
        # the function is declared not when it's called
        func: SAGAFunction = SAGAFunction(stmt, self.env)
        self.env.define(stmt.name.lexeme, func)
        return None
    
    @override
    def visit_break(self, stmt: Break):
        raise BreakException()

    @override
    def visit_continue(self, stmt: Continue):
        raise ContinueException()

    @override
    def visit_while(self, stmt):
        try:
            while self.is_truthful(self.evaluate(stmt.condition)):
                try:
                    self.execute(stmt.body)
                except ContinueException:
                    continue  
                except BreakException:
                    break 
        except BreakException:
            pass  
        return None

    @override
    def visit_if(self, stmt: If):
        if self.is_truthful(self.evaluate(stmt.condition)):
            self.execute_block(stmt.then_branch.statements, self.env)
        elif stmt.else_branch != None:
            self.execute_block(stmt.else_branch.statements, self.env)
        return None

    @override
    def visit_say(self, say: Say):
        value: any = self.evaluate(say.expression)
        print(value)
        return None
    
    @override
    def visit_return(self, stmt):
        value: any = None
        if stmt.value is not None: value = self.evaluate(stmt.value)

        raise ReturnException(value)

    @override
    def visit_let(self, let: Let):
        value: any = None
        if let.initializer is not None:
            value = self.evaluate(let.initializer)
        
        self.env.define(let.name.lexeme, value)
        return None

    def evaluate(self, expr: Expr):
        return expr.accept(self)
    
    def is_truthful(self, object: any):
        if object is None: return False
        if isinstance(object, bool): return bool(object)
        return True
    
    def check_number_operand(self, operator: Token, operand: any):
        if isinstance(operand, (int, float)): return
        raise RuntimeError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator: Token, left: any, right: any):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)): return
        raise RuntimeError(operator, "Operands must be numbers.")