from typing import override

from expr.expr import Visitor, Expr, Binary, Grouping, Unary, Literal 
from lexer.token import Token
from lexer.token_type import TokenType

class AstPrinter(Visitor):
    """Produces a Lisp-like representation of our ASTs"""
    def __init__(self, expr: Expr):
        super().__init__()
        self.expr = expr

    def __repr__(self):
        return self.expr.accept(self)

    @override
    def visit_binary(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    @override
    def visit_grouping(self, expr: Grouping):
        return self.parenthesize("groupe", expr.expression)
    
    @override
    def visit_literal(self, expr: Literal):
        if expr.value == None: return "nil"
        return str(expr.value)
    
    @override
    def visit_unary(self, expr: Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)
    
    def parenthesize(self, name: str, *exprs: Expr):
        output = f"({name}"

        for expr in exprs:
            output += (" " + expr.accept(self)) 
        output += ")"

        return output


if __name__ == '__main__':
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1, 1),
        Grouping(Literal(45.69))
    )

    print(AstPrinter(expression))